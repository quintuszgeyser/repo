"""
BC-4000 Scale Sync Service — CLIENT MODE

Polls PostgreSQL every SYNC_INTERVAL_SEC seconds for changed products
and pushes price updates to the BC-4000 scale via TCP port 7061.

The scale listens on port 7061 when properly configured (B09-23 enabled).
Protocol: Ishida Slp4000, reverse-engineered from SLP-V SlpDbServer.dll.
"""
import json
import logging
import os
import random
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

import psycopg
import psycopg.rows

from bc4000_client import send_chunk, ProtocolError
from plu_formatter import should_sync, format_full_plu, MSG_NO_FULL_PLU

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

SCALE_IP   = os.environ['SCALE_IP']
SCALE_PORT = int(os.environ.get('SCALE_PORT', '7061'))
SCALE_TIMEOUT = int(os.environ.get('SCALE_TIMEOUT_SEC', '10'))

POSTGRES_HOST     = os.environ.get('POSTGRES_HOST', 'localhost')
POSTGRES_PORT     = int(os.environ.get('POSTGRES_PORT', '5432'))
POSTGRES_DB       = os.environ.get('POSTGRES_DB', 'farm_pos_prod')
POSTGRES_USER     = os.environ.get('POSTGRES_USER', 'farmstall')
POSTGRES_PASSWORD = os.environ['POSTGRES_PASSWORD']

SYNC_INTERVAL   = int(os.environ.get('SYNC_INTERVAL_SEC', '60'))
CHUNK_SIZE      = int(os.environ.get('CHUNK_SIZE', '50'))
DRY_RUN         = os.environ.get('DRY_RUN', 'false').lower() == 'true'
FORCE_FULL_SYNC = os.environ.get('FORCE_FULL_SYNC', 'false').lower() == 'true'

DATA_DIR          = Path('/data')
STATE_FILE        = DATA_DIR / 'sync_state.json'
FAILED_FILE       = DATA_DIR / 'failed_products.json'
SUMMARY_FILE      = DATA_DIR / 'sync_summary.json'
HEARTBEAT_FILE    = DATA_DIR / 'last_success.timestamp'
FIRST_SUCCESS_FILE = DATA_DIR / 'first_success.timestamp'

DEAD_LETTER_SKIP_FAILURES   = 5
DEAD_LETTER_SKIP_HOURS      = 1
DEAD_LETTER_PERMANENT_FAILURES = 24

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger('scale_sync')

if DRY_RUN:
    logger.warning('DRY_RUN=true — no data will be sent to scale')
if FORCE_FULL_SYNC:
    logger.warning('FORCE_FULL_SYNC=true — ignoring sync watermark')

# ---------------------------------------------------------------------------
# Atomic file writes
# ---------------------------------------------------------------------------

def _atomic_write(path: Path, data: str):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(data, encoding='utf-8')
    tmp.replace(path)

# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding='utf-8'))
        except Exception as e:
            logger.error(f"Could not read state file: {e}")
    return {'last_sync_watermark': None}


def save_state(state: dict):
    _atomic_write(STATE_FILE, json.dumps(state, default=str, indent=2))


def load_failed() -> dict:
    if FAILED_FILE.exists():
        try:
            return json.loads(FAILED_FILE.read_text(encoding='utf-8'))
        except Exception as e:
            logger.error(f"Could not read failed file: {e}")
    return {}


def save_failed(failed: dict):
    _atomic_write(FAILED_FILE, json.dumps(failed, default=str, indent=2))


def is_dead_letter(product: dict, failed: dict) -> bool:
    rec = failed.get(str(product['id']))
    if not rec:
        return False
    skip_until = rec.get('skip_until')
    if skip_until:
        if datetime.now(timezone.utc) < datetime.fromisoformat(skip_until):
            return True
        rec.pop('skip_until', None)
    return False


def mark_failed(product_id: int, error: str, failed: dict):
    key = str(product_id)
    rec = failed.setdefault(key, {'consecutive_failures': 0, 'last_error': ''})
    rec['consecutive_failures'] = rec.get('consecutive_failures', 0) + 1
    rec['last_error'] = str(error)
    n = rec['consecutive_failures']
    if n >= DEAD_LETTER_PERMANENT_FAILURES:
        logger.error(f"Product {product_id} has failed {n} times — PERMANENT dead-letter.")
        rec['permanent'] = True
    elif n >= DEAD_LETTER_SKIP_FAILURES:
        skip_until = (datetime.now(timezone.utc) + timedelta(hours=DEAD_LETTER_SKIP_HOURS)).isoformat()
        rec['skip_until'] = skip_until
        logger.warning(f"Product {product_id} skipped until {skip_until} after {n} failures")


def reset_failed(product_id: int, failed: dict):
    failed.pop(str(product_id), None)


def write_heartbeat():
    _atomic_write(HEARTBEAT_FILE, datetime.now(timezone.utc).isoformat())


def write_first_success():
    if not FIRST_SUCCESS_FILE.exists():
        _atomic_write(FIRST_SUCCESS_FILE, datetime.now(timezone.utc).isoformat())
        logger.info("First successful sync recorded.")


def write_summary(records_sent: int, updated: int, errors: int, failed: dict):
    skipped = [
        {'id': int(k), 'skip_until': v.get('skip_until'), 'failures': v.get('consecutive_failures')}
        for k, v in failed.items()
        if v.get('skip_until') or v.get('permanent')
    ]
    summary = {
        'last_run': datetime.now(timezone.utc).isoformat(),
        'records_sent': records_sent,
        'records_updated': updated,
        'records_errors': errors,
        'skipped_products': skipped,
    }
    _atomic_write(SUMMARY_FILE, json.dumps(summary, default=str, indent=2))

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

def _db_connect():
    return psycopg.connect(
        host=POSTGRES_HOST, port=POSTGRES_PORT,
        dbname=POSTGRES_DB, user=POSTGRES_USER, password=POSTGRES_PASSWORD,
        connect_timeout=10, row_factory=psycopg.rows.dict_row,
    )


def db_connect_with_retry(retries: int = 10, delay: int = 3):
    for attempt in range(retries):
        try:
            conn = _db_connect()
            logger.info("Database connection established.")
            return conn
        except Exception as e:
            if attempt == retries - 1:
                raise
            logger.warning(f"DB not ready (attempt {attempt+1}/{retries}): {e}")
            time.sleep(delay)


def fetch_products(conn, since: Optional[str]):
    with conn.transaction():
        rows = conn.execute("""
            SELECT id, name, price, price_per_unit, sold_by_weight,
                   is_archived, is_for_sale, product_type, updated_at, barcode
            FROM products
            WHERE (
                %(since)s::timestamptz IS NULL
                OR updated_at > %(since)s::timestamptz - INTERVAL '5 seconds'
            )
            AND is_archived = FALSE
            AND is_for_sale = TRUE
            AND product_type != 'recipe'
            AND (
                (sold_by_weight = FALSE AND price IS NOT NULL AND price > 0)
                OR (sold_by_weight = TRUE  AND price_per_unit IS NOT NULL AND price_per_unit > 0)
            )
            ORDER BY id
        """, {'since': since}).fetchall()
    if not rows:
        return [], None
    watermark = max(r['updated_at'] for r in rows)
    logger.info(f"Fetched {len(rows)} products (since={since}, watermark={watermark})")
    return rows, watermark


def chunked(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


def scale_reachable() -> bool:
    import socket
    try:
        s = socket.create_connection((SCALE_IP, SCALE_PORT), timeout=SCALE_TIMEOUT)
        s.close()
        return True
    except Exception as e:
        logger.error(f"Scale unreachable at {SCALE_IP}:{SCALE_PORT} — {e}")
        return False

# ---------------------------------------------------------------------------
# Main sync cycle
# ---------------------------------------------------------------------------

def run_sync_cycle(conn):
    state = load_state()
    failed = load_failed()

    watermark = None if FORCE_FULL_SYNC else state.get('last_sync_watermark')
    is_first_run = watermark is None

    products, batch_watermark = fetch_products(conn, watermark)
    if not products:
        logger.info("No products to sync.")
        write_heartbeat()
        return

    to_sync = []
    for p in products:
        if not should_sync(p):
            continue
        if is_dead_letter(p, failed):
            logger.debug(f"Skipping dead-letter product {p['id']}")
            continue
        data = format_full_plu(p)
        if data is None:
            mark_failed(p['id'], "format_full_plu returned None", failed)
            continue
        to_sync.append((p, data))

    if not to_sync:
        logger.info("No valid PLU records after filtering.")
        save_failed(failed)
        write_heartbeat()
        return

    logger.info(f"Syncing {len(to_sync)} PLUs to scale ({SCALE_IP}:{SCALE_PORT})")

    if not DRY_RUN and not scale_reachable():
        logger.error("Scale unreachable — aborting sync cycle")
        return

    total_sent = total_updated = total_errors = 0
    new_watermark = None

    for chunk_idx, chunk in enumerate(chunked(to_sync, CHUNK_SIZE)):
        if is_first_run:
            time.sleep(1)

        products_in_chunk = [p for p, _ in chunk]
        data_blobs = [d for _, d in chunk]
        chunk_watermark = max(p['updated_at'] for p in products_in_chunk)

        if DRY_RUN:
            for p, d in chunk:
                logger.info(f"DRY_RUN: PLU {p['id']} → {d.decode('utf-8')[:80]}...")
            new_watermark = chunk_watermark if new_watermark is None else max(new_watermark, chunk_watermark)
            total_sent += len(chunk)
            save_state({'last_sync_watermark': new_watermark.isoformat()})
            continue

        result = None
        last_exc = None
        for attempt in range(3):
            try:
                result = send_chunk(
                    host=SCALE_IP, port=SCALE_PORT, timeout=SCALE_TIMEOUT,
                    msg_no=MSG_NO_FULL_PLU, records=data_blobs,
                )
                break
            except (ProtocolError, Exception) as e:
                last_exc = e
                logger.warning(f"Chunk {chunk_idx} attempt {attempt+1}/3 failed: {e}")
                if attempt < 2:
                    time.sleep((2 ** attempt) + random.uniform(0, 0.5))

        if result is None:
            for p in products_in_chunk:
                mark_failed(p['id'], str(last_exc), failed)
            save_failed(failed)
            logger.error(f"Chunk {chunk_idx} failed after 3 retries: {last_exc}")
            write_heartbeat()
            write_summary(total_sent, total_updated, total_errors + len(chunk), failed)
            return

        total_sent += len(chunk)
        total_updated += result['updated']
        total_errors += result['errors']
        for p in products_in_chunk:
            reset_failed(p['id'], failed)
        new_watermark = chunk_watermark if new_watermark is None else max(new_watermark, chunk_watermark)
        save_state({'last_sync_watermark': new_watermark.isoformat()})
        logger.info(
            f"Chunk {chunk_idx}: sent={len(chunk)} updated={result['updated']} "
            f"errors={result['errors']} {result['duration_ms']:.0f}ms"
        )

    save_failed(failed)
    write_heartbeat()
    write_first_success()
    write_summary(total_sent, total_updated, total_errors, failed)
    logger.info(f"Sync complete: sent={total_sent} updated={total_updated} errors={total_errors}")

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Scale sync service starting (CLIENT MODE)")
    logger.info(f"  Scale:    {SCALE_IP}:{SCALE_PORT}")
    logger.info(f"  Database: {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
    logger.info(f"  Interval: {SYNC_INTERVAL}s  chunk_size={CHUNK_SIZE}")
    logger.info(f"  DRY_RUN={DRY_RUN}  FORCE_FULL_SYNC={FORCE_FULL_SYNC}")

    conn = db_connect_with_retry()

    while True:
        try:
            run_sync_cycle(conn)
        except Exception as e:
            logger.error(f"Sync cycle error: {e}", exc_info=True)
            try:
                conn.close()
            except Exception:
                pass
            try:
                conn = db_connect_with_retry(retries=5, delay=5)
            except Exception as conn_err:
                logger.error(f"Could not reconnect to DB: {conn_err}")

        logger.debug(f"Sleeping {SYNC_INTERVAL}s")
        time.sleep(SYNC_INTERVAL)


if __name__ == '__main__':
    main()

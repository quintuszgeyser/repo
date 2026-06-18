"""
BC-4000 Scale Sync Service

POS is the single source of truth. Scale is a downstream cache.

Polls PostgreSQL every SYNC_INTERVAL_SEC seconds.
Sends only products where sync_to_scale=TRUE and scale_hash differs.
Deletes PLUs on scale that no longer exist in POS (by product_code).

Protocol: Ishida Slp4000 — MsgNo 1001 (send) / 2023 (delete).
"""
import json
import logging
import os
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

import psycopg
import psycopg.rows

from bc4000_client import send_chunk, ProtocolError
from plu_formatter import (
    should_sync, validate_for_scale, format_full_plu, format_delete_plu,
    format_prohibit_plu, compute_scale_hash, ScaleSyncValidationError,
    MSG_NO_FULL_PLU, MSG_NO_DELETE_PLU,
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

SCALE_IP      = os.environ['SCALE_IP']
SCALE_PORT    = int(os.environ.get('SCALE_PORT', '7061'))
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

DATA_DIR       = Path('/data')
SUMMARY_FILE   = DATA_DIR / 'sync_summary.json'
HEARTBEAT_FILE = DATA_DIR / 'last_success.timestamp'

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
    logger.warning('DRY_RUN=true -- no data will be sent to scale')
if FORCE_FULL_SYNC:
    logger.warning('FORCE_FULL_SYNC=true -- ignoring scale_hash (full resync)')

# ---------------------------------------------------------------------------
# Atomic file writes
# ---------------------------------------------------------------------------

def _atomic_write(path: Path, data: str):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(data, encoding='utf-8')
    tmp.replace(path)

def write_heartbeat():
    _atomic_write(HEARTBEAT_FILE, datetime.now(timezone.utc).isoformat())

def write_summary(sent, failed, deleted, orphans):
    _atomic_write(SUMMARY_FILE, json.dumps({
        'last_run': datetime.now(timezone.utc).isoformat(),
        'sent': sent, 'failed': failed,
        'deleted': deleted, 'orphans_detected': orphans,
    }, indent=2))

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

def _db_connect():
    conn = psycopg.connect(
        host=POSTGRES_HOST, port=POSTGRES_PORT,
        dbname=POSTGRES_DB, user=POSTGRES_USER, password=POSTGRES_PASSWORD,
        connect_timeout=10, row_factory=psycopg.rows.dict_row,
        autocommit=True,  # each statement commits immediately — no idle transactions blocking migrations
    )
    return conn

def db_connect_with_retry(retries=10, delay=3):
    for attempt in range(retries):
        try:
            conn = _db_connect()
            logger.info("Database connection established.")
            return conn
        except Exception as e:
            if attempt == retries - 1: raise
            logger.warning(f"DB not ready (attempt {attempt+1}/{retries}): {e}")
            time.sleep(delay)

def fetch_scale_products(conn) -> List[dict]:
    """Fetch all products with sync_to_scale=TRUE (POS master copy).
    Commits after read to release any implicit transaction lock.
    """
    rows = conn.execute("""
        SELECT id, name, price, price_per_unit, sold_by_weight,
               is_archived, is_for_sale, product_type, updated_at,
               barcode, product_code, sync_to_scale,
               scale_tare, scale_shelf_life, scale_pack_qty,
               scale_open_price, scale_msg1, scale_msg2, scale_prohibit,
               scale_hash, scale_last_sync_status
        FROM products
        WHERE sync_to_scale = TRUE
        ORDER BY product_code
    """).fetchall()
    conn.commit()  # release implicit transaction — prevent lock blocking POS migrations
    return rows

def fetch_synced_codes(conn) -> set:
    """Get ALL product_codes ever successfully synced to scale.
    Catches orphans from: archived, sync disabled, type changed, deleted, PLU changed.
    """
    rows = conn.execute("""
        SELECT product_code FROM products
        WHERE scale_last_sync_status IN ('ok', 'plu_changed')
          AND product_code IS NOT NULL
    """).fetchall()
    conn.commit()
    return {r['product_code'] for r in rows}


def fetch_plu_changed(conn) -> list:
    """Get products where PLU was changed — need to remove OLD PLU from scale first."""
    rows = conn.execute("""
        SELECT p.id, p.product_code as new_plu, l.old_plu
        FROM products p
        JOIN scale_plu_log l ON l.product_id = p.id
        WHERE p.scale_last_sync_status = 'plu_changed'
          AND l.sync_cleared = FALSE
          AND l.old_plu IS NOT NULL
        ORDER BY l.changed_at
    """).fetchall()
    conn.commit()
    return rows

def mark_product_synced(conn, product_id: int, scale_hash: str):
    conn.execute("""
        UPDATE products SET
            scale_last_synced_at = NOW(),
            scale_last_sync_status = 'ok',
            scale_last_sync_error = NULL,
            scale_hash = %(hash)s
        WHERE id = %(id)s
    """, {'hash': scale_hash, 'id': product_id})

def mark_product_failed(conn, product_id: int, error: str):
    conn.execute("""
        UPDATE products SET
            scale_last_sync_status = 'error',
            scale_last_sync_error = %(error)s
        WHERE id = %(id)s
    """, {'error': error[:500], 'id': product_id})

def create_sync_run(conn, run_type: str) -> int:
    row = conn.execute("""
        INSERT INTO scale_sync_runs (started_at, run_type, status,
            products_total, products_sent, products_failed, orphans_detected, orphans_removed)
        VALUES (NOW(), %(run_type)s, 'running', 0, 0, 0, 0, 0)
        RETURNING id
    """, {'run_type': run_type}).fetchone()
    return row['id']

def complete_sync_run(conn, run_id: int, status: str, sent=0, failed=0, orphans=0, removed=0, error=None):
    conn.execute("""
        UPDATE scale_sync_runs SET
            completed_at = NOW(),
            status = %(status)s,
            products_sent = %(sent)s,
            products_failed = %(failed)s,
            orphans_detected = %(orphans)s,
            orphans_removed = %(removed)s,
            error_message = %(error)s
        WHERE id = %(id)s
    """, {'status': status, 'sent': sent, 'failed': failed,
          'orphans': orphans, 'removed': removed, 'error': error, 'id': run_id})

# ---------------------------------------------------------------------------
# Scale connectivity
# ---------------------------------------------------------------------------

def scale_reachable() -> bool:
    import socket
    try:
        s = socket.create_connection((SCALE_IP, SCALE_PORT), timeout=SCALE_TIMEOUT)
        s.close()
        return True
    except Exception as e:
        logger.error(f"Scale unreachable at {SCALE_IP}:{SCALE_PORT} -- {e}")
        return False

def _send_with_retry(msg_no, records, label=''):
    for attempt in range(3):
        try:
            return send_chunk(
                host=SCALE_IP, port=SCALE_PORT, timeout=SCALE_TIMEOUT,
                msg_no=msg_no, records=records,
            ), None
        except (ProtocolError, Exception) as e:
            logger.warning(f"{label} attempt {attempt+1}/3 failed: {e}")
            if attempt < 2:
                time.sleep((2 ** attempt) + random.uniform(0, 0.5))
    return None, Exception(f"{label} failed after 3 retries")

def chunked(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

# ---------------------------------------------------------------------------
# Main sync cycle
# ---------------------------------------------------------------------------

def run_sync_cycle(conn):
    products = fetch_scale_products(conn)

    # Build work lists
    to_send    = []   # (product, payload_bytes, hash)
    to_skip    = []   # already in sync
    validation_errors = []

    for p in products:
        # Skip archived/no-price products (clean exit, mark appropriately)
        if p['is_archived'] or not p['is_for_sale']:
            continue

        try:
            validate_for_scale(p)
        except ScaleSyncValidationError as e:
            validation_errors.append((p['id'], str(e)))
            mark_product_failed(conn, p['id'], str(e))
            logger.warning(f"Validation error: {e}")
            continue

        new_hash = compute_scale_hash(p)
        if not FORCE_FULL_SYNC and p.get('scale_hash') == new_hash and p.get('scale_last_sync_status') == 'ok':
            to_skip.append(p['id'])
            continue

        try:
            payload = format_full_plu(p)
        except Exception as e:
            validation_errors.append((p['id'], str(e)))
            mark_product_failed(conn, p['id'], str(e))
            logger.warning(f"Format error for product {p['id']}: {e}")
            continue

        to_send.append((p, payload, new_hash))

    # --- PLU changes: prohibit old PLU before sending new ---
    plu_changes = fetch_plu_changed(conn)
    if plu_changes:
        logger.info(f"PLU changes pending: {[(r['old_plu'], r['new_plu']) for r in plu_changes]}")
        old_plu_records = [format_prohibit_plu(r['old_plu']) for r in plu_changes]
        if DRY_RUN:
            for r in plu_changes:
                logger.info(f"DRY_RUN: prohibit old PLU {r['old_plu']} (changed to {r['new_plu']})")
        elif scale_reachable():
            result, exc = _send_with_retry(MSG_NO_FULL_PLU, old_plu_records, label='prohibit old PLUs')
            if result is not None:
                conn.execute("""
                    UPDATE scale_plu_log SET sync_cleared = TRUE
                    WHERE sync_cleared = FALSE
                      AND old_plu = ANY(%(old_plus)s)
                """, {'old_plus': [r['old_plu'] for r in plu_changes]})
                conn.execute("""
                    UPDATE products SET scale_last_sync_status = NULL, scale_hash = NULL
                    WHERE id = ANY(%(ids)s)
                """, {'ids': [r['id'] for r in plu_changes]})
                logger.info(f"Prohibited {len(plu_changes)} old PLUs, products queued for resync")
            else:
                logger.error(f"Failed to prohibit old PLUs: {exc}")

    # Detect orphans: PLUs previously synced that no longer have sync_to_scale=TRUE
    synced_codes = fetch_synced_codes(conn)
    active_codes = {p['product_code'] for p in products if p.get('product_code')}
    orphan_codes = synced_codes - active_codes

    if to_skip:
        logger.info(f"In sync (skipped): {len(to_skip)} products")
    if not to_send and not orphan_codes and not plu_changes:
        logger.info("No changes to sync.")
        write_heartbeat()
        write_summary(0, 0, 0, 0)
        return

    logger.info(f"Pending: {len(to_send)} products to send, {len(orphan_codes)} orphans to delete")

    if not DRY_RUN and not scale_reachable():
        logger.error("Scale unreachable -- aborting sync cycle")
        return

    run_id = create_sync_run(conn, 'full' if FORCE_FULL_SYNC else 'incremental')
    conn.commit()  # persist run record immediately

    total_sent = total_failed = 0

    # --- Send updated PLUs ---
    for chunk in chunked(to_send, CHUNK_SIZE):
        products_in_chunk = [p for p, _, _ in chunk]
        payloads          = [pl for _, pl, _ in chunk]
        hashes            = {p['id']: h for p, _, h in chunk}

        if DRY_RUN:
            for p, pl, h in chunk:
                logger.info(f"DRY_RUN: send PLU {p['product_code']} ({p['name']})")
                mark_product_synced(conn, p['id'], h)
            total_sent += len(chunk)
            conn.commit()
            continue

        result, exc = _send_with_retry(MSG_NO_FULL_PLU, payloads, label=f'send chunk')
        if result is None:
            for p in products_in_chunk:
                mark_product_failed(conn, p['id'], str(exc))
                total_failed += 1
            conn.commit()
            logger.error(f"Chunk send failed: {exc}")
        else:
            for p in products_in_chunk:
                mark_product_synced(conn, p['id'], hashes[p['id']])
                total_sent += 1
            conn.commit()
            logger.info(f"Sent {len(chunk)} PLUs: updated={result['updated']} errors={result['errors']} {result['duration_ms']:.0f}ms")

    # --- Remove orphan PLUs by overwriting with a zeroed/disabled record ---
    # MsgNo 2023 (delete) is unreliable — scale returns status 20 for some PLUs.
    # Instead we overwrite with a zero-price "REMOVED" record using MsgNo 1001.
    orphans_removed = 0
    if orphan_codes:
        logger.info(f"Prohibiting {len(orphan_codes)} orphan PLUs on scale: {sorted(orphan_codes)}")
        # Use prohibit format: REMOVED, price=0, barcode disabled — safer than zero-out
        zero_records = [format_prohibit_plu(code) for code in sorted(orphan_codes)]

        if DRY_RUN:
            for code in sorted(orphan_codes):
                logger.info(f"DRY_RUN: zero-out PLU {code}")
            orphans_removed = len(orphan_codes)
        else:
            result, exc = _send_with_retry(MSG_NO_FULL_PLU, zero_records, label='zero orphans')
            if result is not None:
                orphans_removed = len(orphan_codes)
                conn.execute("""
                    UPDATE products SET scale_last_sync_status = 'removed'
                    WHERE product_code = ANY(%(codes)s)
                """, {'codes': list(orphan_codes)})
                conn.commit()
                logger.info(f"Zeroed {orphans_removed} orphan PLUs on scale")
            else:
                logger.error(f"Orphan zero-out failed: {exc}")

    complete_sync_run(conn, run_id, 'ok' if total_failed == 0 else 'partial',
                      sent=total_sent, failed=total_failed,
                      orphans=len(orphan_codes), removed=orphans_removed)
    conn.commit()
    write_heartbeat()
    write_summary(total_sent, total_failed, orphans_removed, len(orphan_codes))
    logger.info(f"Sync complete: sent={total_sent} failed={total_failed} orphans_removed={orphans_removed}")

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Scale sync service starting")
    logger.info(f"  Scale:    {SCALE_IP}:{SCALE_PORT}")
    logger.info(f"  Database: {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
    logger.info(f"  Interval: {SYNC_INTERVAL}s  DRY_RUN={DRY_RUN}  FORCE_FULL_SYNC={FORCE_FULL_SYNC}")

    conn = db_connect_with_retry()

    while True:
        try:
            run_sync_cycle(conn)
        except Exception as e:
            logger.error(f"Sync cycle error: {e}", exc_info=True)
            try: conn.close()
            except Exception: pass
            try: conn = db_connect_with_retry(retries=5, delay=5)
            except Exception as ce: logger.error(f"Could not reconnect: {ce}")

        logger.debug(f"Sleeping {SYNC_INTERVAL}s")
        time.sleep(SYNC_INTERVAL)

if __name__ == '__main__':
    main()

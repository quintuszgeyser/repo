"""
BC-4000 Scale Sync Service — SERVER MODE

The scale connects TO us (port 7061) when the operator triggers P23-03-01
(PLU file receive) on the scale's front panel. We listen, and when the scale
connects we push all current PLU data.

Protocol: Ishida Slp4000, reverse-engineered from SLP-V SlpDbServer.dll.
"""
import json
import logging
import os
import socket
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

import psycopg
import psycopg.rows

from bc4000_client import send_on_socket, ProtocolError
from plu_formatter import should_sync, format_full_plu, MSG_NO_FULL_PLU

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

LISTEN_HOST = os.environ.get('LISTEN_HOST', '0.0.0.0')
LISTEN_PORT = int(os.environ.get('SCALE_PORT', '7061'))
SCALE_TIMEOUT = int(os.environ.get('SCALE_TIMEOUT_SEC', '30'))

POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = int(os.environ.get('POSTGRES_PORT', '5432'))
POSTGRES_DB = os.environ.get('POSTGRES_DB', 'farm_pos_prod')
POSTGRES_USER = os.environ.get('POSTGRES_USER', 'farmstall')
POSTGRES_PASSWORD = os.environ['POSTGRES_PASSWORD']

DRY_RUN = os.environ.get('DRY_RUN', 'false').lower() == 'true'

DATA_DIR = Path('/data')
SUMMARY_FILE = DATA_DIR / 'sync_summary.json'
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
    logger.warning('DRY_RUN=true — no data will be sent to scale')

# ---------------------------------------------------------------------------
# Atomic file writes
# ---------------------------------------------------------------------------

def _atomic_write(path: Path, data: str):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(data, encoding='utf-8')
    tmp.replace(path)


def write_heartbeat():
    _atomic_write(HEARTBEAT_FILE, datetime.now(timezone.utc).isoformat())


def write_summary(sent: int, updated: int, errors: int, scale_addr: str):
    summary = {
        'last_run': datetime.now(timezone.utc).isoformat(),
        'scale_address': scale_addr,
        'records_sent': sent,
        'records_updated': updated,
        'records_errors': errors,
    }
    _atomic_write(SUMMARY_FILE, json.dumps(summary, default=str, indent=2))


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

def _db_connect():
    return psycopg.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        connect_timeout=10,
        row_factory=psycopg.rows.dict_row,
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


def fetch_all_products(conn) -> List[dict]:
    """Fetch all active, syncable products."""
    rows = conn.execute("""
        SELECT id, name, price, price_per_unit, sold_by_weight,
               is_archived, is_for_sale, product_type, updated_at
        FROM products
        WHERE is_archived = FALSE
          AND is_for_sale = TRUE
          AND product_type != 'recipe'
          AND (
              (sold_by_weight = FALSE AND price IS NOT NULL AND price > 0)
              OR (sold_by_weight = TRUE  AND price_per_unit IS NOT NULL AND price_per_unit > 0)
          )
        ORDER BY id
    """).fetchall()
    return rows


# ---------------------------------------------------------------------------
# Handle one scale connection
# ---------------------------------------------------------------------------

def handle_connection(conn_sock: socket.socket, addr: tuple, db_conn):
    scale_addr = f"{addr[0]}:{addr[1]}"
    logger.info(f"Scale connected from {scale_addr}")

    try:
        products = fetch_all_products(db_conn)
        records = []
        for p in products:
            if not should_sync(p):
                continue
            data = format_full_plu(p)
            if data is None:
                logger.warning(f"Could not format PLU {p['id']} — skipping")
                continue
            records.append((p, data))

        if not records:
            logger.info("No products to send.")
            return

        logger.info(f"Sending {len(records)} PLUs to scale at {scale_addr}")

        if DRY_RUN:
            for p, d in records:
                logger.info(f"DRY_RUN: PLU {p['id']} → {d.decode('utf-8')[:80]}...")
            write_heartbeat()
            write_summary(len(records), 0, 0, scale_addr)
            return

        data_blobs = [d for _, d in records]
        result = send_on_socket(
            sock=conn_sock,
            timeout=SCALE_TIMEOUT,
            msg_no=MSG_NO_FULL_PLU,
            records=data_blobs,
        )

        write_heartbeat()
        write_summary(len(records), result['updated'], result['errors'], scale_addr)
        logger.info(
            f"Sync complete: sent={len(records)} updated={result['updated']} "
            f"errors={result['errors']} {result['duration_ms']:.0f}ms"
        )

    except (ProtocolError, Exception) as e:
        logger.error(f"Error during sync with {scale_addr}: {e}", exc_info=True)
    finally:
        conn_sock.close()
        logger.info(f"Connection from {scale_addr} closed.")


# ---------------------------------------------------------------------------
# Main — TCP server loop
# ---------------------------------------------------------------------------

def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    logger.info(f"Scale sync service starting (SERVER MODE)")
    logger.info(f"  Listening: {LISTEN_HOST}:{LISTEN_PORT}")
    logger.info(f"  Database:  {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
    logger.info(f"  DRY_RUN={DRY_RUN}")
    logger.info(f"  Waiting for scale to connect on port {LISTEN_PORT}...")

    db_conn = db_connect_with_retry()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((LISTEN_HOST, LISTEN_PORT))
    server.listen(1)

    while True:
        try:
            conn_sock, addr = server.accept()
            try:
                db_conn.execute("SELECT 1")
            except Exception:
                logger.warning("DB connection lost, reconnecting...")
                try:
                    db_conn.close()
                except Exception:
                    pass
                db_conn = db_connect_with_retry(retries=5, delay=5)

            handle_connection(conn_sock, addr, db_conn)

        except Exception as e:
            logger.error(f"Server loop error: {e}", exc_info=True)
            time.sleep(1)


if __name__ == '__main__':
    main()

"""
BC-4000 scale TCP/IP client — protocol confirmed via Wireshark captures 2026-06-23.

Architecture: PC connects OUT to scale:7061 (scale is the server).

Message types confirmed:
  MsgNo 0026 — Status poll + delete
  MsgNo 1001 — Full PLU push
  MsgNo 1024 — Keyboard presets
  MsgNo 1029 — Advertisement messages

Frame format (all messages):
  Header   (8 bytes): MsgNo(2 BCD) + 00 00 00 00 + record_count(2 uint16)
  Per record:
    Subheader (8 bytes): MsgNo(2 BCD) + is_first(1) + 00 00 00 + data_size(2 uint16)
    Data:                CSV bytes

Scale response (20 bytes, sent after every ~80 records and at end):
  Bytes  0-1: MsgNo BCD (echo)
  Bytes  2-7: flags / padding
  Bytes  8-11: 00 00 00 00
  Bytes 12-13: records updated (uint16)
  Bytes 14-15: records total in batch (uint16)
  Bytes 16-19: 00 00 00 00

After each 20-byte scale response, PC must send an 8-byte ack:
  MsgNo(2 BCD) + 00 00 00 00 + cumulative_records_acked(2 uint16)
"""
import logging
import select
import socket
import struct
import time
from typing import List

logger = logging.getLogger('bc4000_client')

MSG_NO_PLU_SEND   = 1001
MSG_NO_STATUS     = 26
MSG_NO_KEYBOARD   = 1024
MSG_NO_ADVERT     = 1029

BATCH_SIZE = 80  # scale sends a mid-ack every ~80 records


class ProtocolError(Exception):
    pass


# ---------------------------------------------------------------------------
# Encoding helpers
# ---------------------------------------------------------------------------

def num2bcd(value: int, num_digits: int) -> bytes:
    """Pack integer into packed BCD. num2bcd(1001, 4) == b'\\x10\\x01'"""
    num_bytes = (num_digits + 1) // 2
    result = bytearray(num_bytes)
    pos = num_bytes - 1
    for i in range(num_digits, 0, -1):
        digit = value % 10
        value //= 10
        if (num_digits - i) % 2 == 0:
            result[pos] = digit
        else:
            result[pos] |= (digit << 4)
            pos -= 1
    return bytes(result)


def bcd2num(data: bytes, offset: int, num_digits: int):
    """Decode packed BCD → (value, new_offset)."""
    num_bytes = (num_digits + 1) // 2
    result = 0
    for i in range(num_bytes):
        b = data[offset + i]
        result = result * 100 + ((b >> 4) & 0x0F) * 10 + (b & 0x0F)
    if num_digits % 2 == 1:
        result //= 10
    return result, offset + num_bytes


# ---------------------------------------------------------------------------
# Socket helpers
# ---------------------------------------------------------------------------

def _recv_exact(sock: socket.socket, n: int) -> bytes:
    buf = bytearray()
    while len(buf) < n:
        try:
            chunk = sock.recv(n - len(buf))
        except socket.timeout:
            raise ProtocolError(f"Timeout waiting for {n - len(buf)} more bytes")
        if not chunk:
            raise ProtocolError("Connection closed by scale before all bytes received")
        buf.extend(chunk)
    return bytes(buf)


def _has_data(sock: socket.socket, timeout: float = 0.05) -> bool:
    r, _, _ = select.select([sock], [], [], timeout)
    return bool(r)


# ---------------------------------------------------------------------------
# Protocol framing
# ---------------------------------------------------------------------------

def _build_header(msg_no: int, record_count: int) -> bytes:
    """8-byte header: MsgNo(2 BCD) + 00 00 00 00 + record_count(2 uint16)"""
    hdr = bytearray(8)
    hdr[0:2] = num2bcd(msg_no, 4)
    struct.pack_into('>H', hdr, 6, record_count)
    return bytes(hdr)


def _build_subheader(msg_no: int, data_size: int, is_first: bool = False) -> bytes:
    """8-byte subheader: MsgNo(2 BCD) + is_first(1) + 00 00 00 + data_size(2 uint16)"""
    sub = bytearray(8)
    sub[0:2] = num2bcd(msg_no, 4)
    sub[2] = 1 if is_first else 0
    struct.pack_into('>H', sub, 6, data_size)
    return bytes(sub)


def _build_ack(msg_no: int, cumulative_records: int) -> bytes:
    """8-byte PC ack after each scale mid-response."""
    ack = bytearray(8)
    ack[0:2] = num2bcd(msg_no, 4)
    struct.pack_into('>H', ack, 6, cumulative_records)
    return bytes(ack)


def _parse_response(raw: bytes) -> dict:
    """Parse 20-byte scale response."""
    if len(raw) < 20:
        raise ProtocolError(f"Short response: expected 20 bytes, got {len(raw)}")
    msg_no, _ = bcd2num(raw, 0, 4)
    updated = struct.unpack_from('>H', raw, 12)[0]
    total   = struct.unpack_from('>H', raw, 14)[0]
    return {'msg_no': msg_no, 'updated': updated, 'total': total}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def poll_status(host: str, port: int, timeout: int) -> dict:
    """
    MsgNo 0026 status poll — returns PLU count on scale.
    Also used to delete a single PLU: include plu_no in extra_data.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.settimeout(timeout)
        sock.connect((host, port))
        sock.sendall(_build_header(MSG_NO_STATUS, 18))
        raw = _recv_exact(sock, 20)
        resp = _parse_response(raw)
        plu_count = resp['updated']
        sock.sendall(_build_ack(MSG_NO_STATUS, 2))
    finally:
        sock.close()
    return {'plu_count': plu_count}


def send_chunk(
    host: str,
    port: int,
    timeout: int,
    msg_no: int,
    records: List[bytes],
) -> dict:
    """
    Send a batch of records to the BC-4000 scale.

    Protocol (confirmed from Wireshark):
      connect → header(8) → [subheader(8) + data] × N
      → scale sends 20-byte mid-acks every ~80 records
      → PC sends 8-byte ack after each mid-ack
      → final 20-byte response from scale
      → disconnect

    Returns: dict with keys: updated, errors, duration_ms
    """
    if not records:
        return {'updated': 0, 'errors': 0, 'duration_ms': 0}

    t0 = time.monotonic()
    total_updated = 0
    total_acked = 0

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.settimeout(timeout)
        sock.connect((host, port))
        logger.debug(f"Connected to {host}:{port} for MsgNo {msg_no}, {len(records)} records")

        # Send main header with total record count
        sock.sendall(_build_header(msg_no, len(records)))

        # Send all records, draining mid-acks as they arrive
        for i, rec in enumerate(records):
            sock.sendall(_build_subheader(msg_no, len(rec), is_first=(i == 0)))
            sock.sendall(rec)

            # After each batch boundary, drain any mid-ack from scale
            if (i + 1) % BATCH_SIZE == 0 and _has_data(sock):
                raw = _recv_exact(sock, 20)
                resp = _parse_response(raw)
                if resp['msg_no'] != msg_no:
                    raise ProtocolError(f"MsgNo mismatch in mid-ack: {resp['msg_no']}")
                total_updated += resp['updated']
                total_acked += resp['updated']
                logger.debug(f"Mid-ack: updated={resp['updated']} cumulative={total_acked}")
                sock.sendall(_build_ack(msg_no, total_acked))

        # Drain any remaining mid-acks, then read final response
        responses_needed = max(1, len(records) // BATCH_SIZE + 1)
        remaining = len(records) - total_acked
        while remaining > 0:
            raw = _recv_exact(sock, 20)
            resp = _parse_response(raw)
            if resp['msg_no'] != msg_no:
                raise ProtocolError(f"MsgNo mismatch in response: {resp['msg_no']}")
            total_updated += resp['updated']
            total_acked += resp['total'] if resp['total'] > 0 else resp['updated']
            remaining = len(records) - total_acked
            logger.debug(f"Response: updated={resp['updated']} total={resp['total']} remaining={remaining}")
            if remaining > 0:
                sock.sendall(_build_ack(msg_no, total_acked))

    finally:
        sock.close()

    duration_ms = (time.monotonic() - t0) * 1000
    logger.debug(f"MsgNo {msg_no}: {len(records)} records, updated={total_updated}, {duration_ms:.0f}ms")
    return {
        'updated': total_updated,
        'errors': 0,
        'duration_ms': duration_ms,
    }

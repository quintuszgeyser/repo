"""
BC-4000 scale TCP/IP client using the Slp4000 protocol.

Protocol reverse-engineered from Ishida SLP-V SlpDbServer.dll (decompiled with dnSpy).
Port: 7061
Encoding: packed BCD for integers, big-endian uint32/uint16 for sizes.
"""
import logging
import socket
import struct
import time
from typing import List

logger = logging.getLogger('bc4000_client')

# Number of initial cycles to log raw hex (for protocol offset validation)
_HEX_LOG_CYCLES_REMAINING = 3


class ProtocolError(Exception):
    pass


# ---------------------------------------------------------------------------
# Encoding helpers (direct ports of SlpConvert methods)
# ---------------------------------------------------------------------------

def num2bcd(value: int, num_digits: int) -> bytes:
    """
    Pack an integer into BCD (Binary Coded Decimal), num_digits digits.

    From Num2Bcd() in SlpConvert:
      num2bcd(1001, 4) == b'\\x10\\x01'
      num2bcd(1234, 4) == b'\\x12\\x34'
    """
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
    """Decode packed BCD → (value, new_offset). From Bcd2Num() in SlpConvert."""
    num_bytes = (num_digits + 1) // 2
    result = 0
    for i in range(num_bytes):
        b = data[offset + i]
        result = result * 100 + ((b >> 4) & 0x0F) * 10 + (b & 0x0F)
    if num_digits % 2 == 1:
        result //= 10
    return result, offset + num_bytes


def num2nl(value: int) -> bytes:
    """Big-endian uint32. From Num2nl() in SlpConvert."""
    return struct.pack('>I', value)


def num2ns(value: int) -> bytes:
    """Big-endian uint16. From Num2ns() in SlpConvert."""
    return struct.pack('>H', value)


def nl2num(data: bytes, offset: int):
    """Decode big-endian uint32 → (value, new_offset). From Nl2Num()."""
    return struct.unpack_from('>I', data, offset)[0], offset + 4


def ns2num(data: bytes, offset: int):
    """Decode big-endian uint16 → (value, new_offset). From Ns2Num()."""
    return struct.unpack_from('>H', data, offset)[0], offset + 2


# ---------------------------------------------------------------------------
# Low-level socket helpers
# ---------------------------------------------------------------------------

def _recv_exact(sock: socket.socket, n: int) -> bytes:
    """Receive exactly n bytes; raises ProtocolError on close or timeout."""
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


# ---------------------------------------------------------------------------
# Protocol framing
# ---------------------------------------------------------------------------

def _build_header(msg_no: int, total_payload_size: int) -> bytes:
    """
    8-byte send header (SendHeader in Slp4000Scale):
      Bytes 0-1: MsgNo as BCD (4 digits)
      Bytes 2-3: 0x00
      Bytes 4-7: (total_payload_size + 8) as big-endian uint32
    """
    hdr = bytearray(8)
    hdr[0:2] = num2bcd(msg_no, 4)
    hdr[4:8] = num2nl(total_payload_size + 8)
    return bytes(hdr)


def _build_subheader(msg_no: int, data_size: int, is_first: bool) -> bytes:
    """
    8-byte sub-header (SendSubHeader in Slp4000Scale):
      Bytes 0-1: MsgNo as BCD (4 digits)
      Byte  2:   1 if first record in chunk, else 0
      Bytes 3-5: 0x00
      Bytes 6-7: data_size as big-endian uint16
    """
    sub = bytearray(8)
    sub[0:2] = num2bcd(msg_no, 4)
    sub[2] = 1 if is_first else 0
    sub[6:8] = num2ns(data_size)
    return bytes(sub)


def _parse_response_header(raw: bytes) -> dict:
    """
    8-byte response header (ConvertHeaderToBin in Slp4000Scale, non-Astra path):
      Bytes 0-1: MsgNo as BCD (4 digits) → 2 bytes, offset advances by 2
      Bytes 2-3: DeviceType as BCD (2 digits) → 1 byte, offset advances by 1 (but parsed as 2-digit BCD)
      Byte  5:   Result (raw byte, 0 = success)
      Bytes 4-7: total_size as big-endian uint32

    Decompiled code:
      header.m_nMsgNo      = Bcd2Num(buf, ref num, 4)   → reads 2 bytes, num=2
      header.m_nDeviceType = Bcd2Num(buf, ref num, 2)   → reads 1 byte, num=3
      header.m_nResult     = buf[num]; num++             → byte 3, num=4
      header.m_nSize       = Nl2Num(buf, ref num)        → bytes 4-7
    """
    offset = 0
    msg_no, offset = bcd2num(raw, offset, 4)       # offset=2
    device_type, offset = bcd2num(raw, offset, 2)  # offset=3
    result = raw[offset]; offset += 1              # offset=4
    total_size, offset = nl2num(raw, offset)       # offset=8
    return {
        'msg_no': msg_no,
        'device_type': device_type,
        'result': result,
        'total_size': total_size,
    }


def _parse_response_body(raw: bytes) -> dict:
    """
    12-byte response body (ConvertResponseToBin, nFlg=0, non-Astra):
      Byte  0:   Status as BCD (2 digits, 1 byte)
      Bytes 1-3: skip (3 bytes)
      Bytes 4-5: RecordsReceived as BCD (4 digits, 2 bytes)
      Bytes 6-7: RecordsUpdated as BCD (4 digits, 2 bytes)
      Bytes 8-9: RecordsWithErrors as BCD (4 digits, 2 bytes)
      Bytes 10-11: ErrorCode as big-endian uint16
    """
    offset = 0
    status, offset = bcd2num(raw, offset, 2)          # offset=1
    offset += 3                                        # skip → offset=4
    received, offset = bcd2num(raw, offset, 4)        # offset=6
    updated, offset = bcd2num(raw, offset, 4)         # offset=8
    errors, offset = bcd2num(raw, offset, 4)          # offset=10
    error_code, offset = ns2num(raw, offset)           # offset=12
    return {
        'status': status,
        'records_received': received,
        'records_updated': updated,
        'records_errors': errors,
        'error_code': error_code,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def send_chunk(
    host: str,
    port: int,
    timeout: int,
    msg_no: int,
    records: List[bytes],
) -> dict:
    """
    Send a batch of PLU records to the BC-4000 scale in a single TCP session.

    Follows the Slp4000Scale.DoSendOp() protocol exactly:
      connect → header → (subheader + data) × N → recv header → recv response → disconnect

    Args:
        host:    Scale IP address
        port:    TCP port (7061)
        timeout: Socket timeout in seconds
        msg_no:  Message number (1040 = price change, 1001 = full PLU)
        records: List of UTF-8 encoded CSV payloads, one per PLU

    Returns:
        dict with keys: updated, errors, error_code, duration_ms

    Raises:
        ProtocolError on any framing, validation, or scale-reported error
    """
    global _HEX_LOG_CYCLES_REMAINING

    if not records:
        return {'updated': 0, 'errors': 0, 'error_code': 0, 'duration_ms': 0}

    # Per-record size guard
    for rec in records:
        if len(rec) > 60_000:
            raise ValueError(f"Record too large for protocol: {len(rec)} bytes")

    # Total payload = N × subheader(8) + sum(data sizes)
    total_payload = sum(8 + len(r) for r in records)

    # Total payload sanity cap
    if total_payload > 1_000_000:
        raise ValueError(f"Chunk payload too large: {total_payload} bytes")

    t0 = time.monotonic()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.settimeout(timeout)
        sock.connect((host, port))
        logger.debug(f"Connected to {host}:{port}")

        # Send header
        sock.sendall(_build_header(msg_no, total_payload))

        # Send subheader + data for each record
        for i, rec in enumerate(records):
            sock.sendall(_build_subheader(msg_no, len(rec), is_first=(i == 0)))
            sock.sendall(rec)

        # Receive response header (8 bytes)
        raw_hdr = _recv_exact(sock, 8)
        if _HEX_LOG_CYCLES_REMAINING > 0:
            logger.debug(f"Response header hex: {raw_hdr.hex()}")
            _HEX_LOG_CYCLES_REMAINING -= 1

        resp_hdr = _parse_response_header(raw_hdr)
        logger.debug(f"Response header: {resp_hdr}")

        # Validate response header
        if resp_hdr['msg_no'] != msg_no:
            raise ProtocolError(
                f"MsgNo mismatch: sent {msg_no}, got {resp_hdr['msg_no']}"
            )
        if resp_hdr['result'] != 0:
            raise ProtocolError(
                f"Scale returned error result: {resp_hdr['result']}"
            )

        # Receive response body (12 bytes)
        raw_body = _recv_exact(sock, 12)
        resp_body = _parse_response_body(raw_body)
        logger.debug(f"Response body: {resp_body}")

        # Validate response body
        if resp_body['status'] != 0:
            raise ProtocolError(f"Scale status error: {resp_body['status']}")
        if resp_body['records_received'] != len(records):
            raise ProtocolError(
                f"RecordsReceived mismatch: sent {len(records)}, "
                f"scale ack'd {resp_body['records_received']}"
            )
        if resp_body['records_errors'] != 0:
            raise ProtocolError(
                f"Scale reported {resp_body['records_errors']} record errors"
            )
        if resp_body['error_code'] != 0:
            raise ProtocolError(
                f"Scale returned non-zero error_code: {resp_body['error_code']}"
            )

    finally:
        sock.close()

    duration_ms = (time.monotonic() - t0) * 1000
    return {
        'updated': resp_body['records_updated'],
        'errors': resp_body['records_errors'],
        'error_code': resp_body['error_code'],
        'duration_ms': duration_ms,
    }

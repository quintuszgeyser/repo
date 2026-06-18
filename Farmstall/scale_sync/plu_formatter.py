"""
PLU data formatting and product filtering for BC-4000 scale sync.

POS is the single source of truth. Scale is a downstream cache.
This module formats POS product data for the scale protocol.

MsgNo 1001: full PLU send — CSV with embedded Ishida description control codes
MsgNo 2023: delete PLU — payload: "{plu_no},"

Field sequence derived from decompiling SLP-V SlpDbServer.dll
SerializeScaleDataAc4000(), South Africa path (IsLongPluBc4000Country=True).
"""
import hashlib
import logging
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

logger = logging.getLogger('plu_formatter')

MSG_NO_FULL_PLU    = 1001
MSG_NO_DELETE_PLU  = 2023  # payload: "{plu_no}," — captured from SLP-V traffic
MSG_NO_PRICE_CHANGE = 1040

MAX_PLU_NO   = 99_999
MAX_NAME_LEN = 20


class ScaleSyncValidationError(Exception):
    pass


def validate_for_scale(product: dict):
    """Raise ScaleSyncValidationError if product cannot be safely sent to scale.
    POS is the master — any invalid state is a POS data problem, not a scale problem.
    """
    pid = product.get('id', '?')

    if not product.get('sync_to_scale'):
        raise ScaleSyncValidationError(f"Product {pid}: sync_to_scale is False")

    if product.get('is_archived'):
        raise ScaleSyncValidationError(f"Product {pid}: is archived")

    if not product.get('is_for_sale'):
        raise ScaleSyncValidationError(f"Product {pid}: not for sale")

    plu_no = product.get('product_code')
    if not plu_no:
        raise ScaleSyncValidationError(
            f"Product {pid} ('{product.get('name')}') has no product_code. "
            f"Cannot send to scale — would use database id which is wrong."
        )
    if plu_no <= 0 or plu_no > MAX_PLU_NO:
        raise ScaleSyncValidationError(
            f"Product {pid}: product_code {plu_no} out of range (1-{MAX_PLU_NO})"
        )

    if product.get('sold_by_weight'):
        ppu = product.get('price_per_unit')
        if not ppu or Decimal(str(ppu)) <= 0:
            raise ScaleSyncValidationError(f"Product {pid}: no valid price_per_unit")
    else:
        price = product.get('price')
        if not price or Decimal(str(price)) <= 0:
            raise ScaleSyncValidationError(f"Product {pid}: no valid price")

    name = (product.get('name') or '').strip()
    if not name:
        raise ScaleSyncValidationError(f"Product {pid}: empty name")


def should_sync(product: dict) -> bool:
    """Return True if product should be sent to scale. Logs reason if skipped."""
    try:
        validate_for_scale(product)
        return True
    except ScaleSyncValidationError as e:
        logger.debug(str(e))
        return False


def price_cents(product: dict) -> int:
    """Return scale price in whole cents.
    Weight items: price_per_unit (R/g) × 100000 = cents/kg
    Fixed items:  price (R) × 100 = cents
    """
    if product.get('sold_by_weight'):
        ppu = Decimal(str(product['price_per_unit']))
        return int((ppu * Decimal('100000')).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
    else:
        p = Decimal(str(product['price']))
        return int((p * Decimal('100')).quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def compute_scale_hash(product: dict) -> str:
    """Deterministic SHA-256 of scale-relevant product fields.
    If this hash matches scale_hash in the DB, the product is in sync.
    """
    tare_raw = product.get('scale_tare')
    parts = [
        str(product.get('product_code', '')),
        (product.get('name') or '').strip().upper()[:MAX_NAME_LEN],
        str(price_cents(product)),
        str(1 if product.get('sold_by_weight') else 0),
        str(float(tare_raw) if tare_raw is not None else 0),  # normalise Decimal/float → str
        str(product.get('scale_shelf_life') or 0),
        str(1 if product.get('scale_open_price') else 0),
        str((product.get('scale_msg1') or '').strip()[:20]),
        str((product.get('scale_msg2') or '').strip()[:20]),
        str(1 if product.get('scale_prohibit') else 0),
    ]
    return hashlib.sha256('|'.join(parts).encode()).hexdigest()


def format_full_plu(product: dict) -> bytes:
    """Format product as MsgNo 1001 CSV for BC-4000.

    Raises ScaleSyncValidationError if product_code is missing — no silent fallback
    to database id (that bug caused PLU 20 when product_code should have been 1).
    """
    validate_for_scale(product)

    plu_no     = product['product_code']   # NEVER use product['id'] here
    sales_mode = 0 if product.get('sold_by_weight') else 1
    price      = price_cents(product)
    name       = (product.get('name') or '')[:MAX_NAME_LEN].upper().replace('"', '""')
    unit_line  = 'PER KG' if product.get('sold_by_weight') else 'EACH'
    desc       = f'\x0d\x0a{name}\x0d\x01{unit_line}'
    price_s    = str(price)

    # Barcode: product_code encoded in scale variable-weight label
    barcode      = str(plu_no)
    barcode_type = '21'   # BarCodeNum=21 (EAN enabled, from SLP-V db)
    pos_flag     = '20'   # Posflag=20 (POS barcode enabled, from SLP-V db)

    # Scale-specific overrides from product
    tare         = str(int(float(product.get('scale_tare') or 0) * 1000))  # g → mg for protocol
    shelf_life   = str(product.get('scale_shelf_life') or 0)
    # BestBeforeFlag: set to 1 (Reference) when shelf_life is set, so scale prints best-before date
    best_before_flag = '1' if (product.get('scale_shelf_life') or 0) > 0 else '0'
    open_price = '1' if product.get('scale_open_price') else '0'
    # Messages stored as text — append to description if set
    msg1_text  = (product.get('scale_msg1') or '').strip()[:20]
    msg2_text  = (product.get('scale_msg2') or '').strip()[:20]
    if msg1_text:
        desc += f'\x0d\x01{msg1_text}'
    if msg2_text:
        desc += f'\x0d\x01{msg2_text}'

    fields = [
        str(plu_no),       # F0   PLU number = product_code (NOT database id)
        str(plu_no),       # F67  item code = same as PLU (encoded in barcode)
        best_before_flag,  # DateFlag / BestBeforeFlag (1=Reference, enables shelf life)
        '0',               # F5   time flag
        '0',           # skip
        '0',           # F46  pack time offset
        '0',           # skip
        '0',           # F8   expiry time flag
        '0',           # skip
        '0',           # num3 date flag part 3
        shelf_life,    # F45  shelf life days
        '0',           # num2 date flag part 2
        '0',           # num4 date flag part 4
        '0', '0', '0', '0',
        '0',           # F59  label format 1
        '0',           # F60  label format 2
        '0', '0', '0', '0',
        '0',           # F71  dept code
        '0',           # F72  group code
        '0', '0', '0',
        '0',           # ExMsg1 (text appended to description instead)
        '0',           # ExMsg2
        '0',           # ExMsg3
        '0',           # Coupon
        '0', '0',
        '0',           # skip
        '0',           # F65  cost price
        '0',           # F117 tax rate
        '0', '0', '0', '0', '0',
        '0',           # skip F10
        '0', '0',
        open_price,    # F7   open price flag
        '0',           # nutrition
        '0',           # F55
        '0',           # F9
        f'"{desc}"',   # F94  description
        str(sales_mode),  # F2  sales mode
        price_s,       # F62  price
        price_s,       # F62  price (duplicate)
        '0',           # F3   markdown flag
        '0',           # F66  markdown price
        '0',           # skip
        '0',           # F42  pack quantity (removed)
        '0',           # F17  unit type
        '0',           # F64  fixed weight
        '0',           # F69  upper weight limit
        '0',           # F70  lower weight limit
        tare,          # F43  tare weight
        '0', '0', '0', '0',
        '0',           # F6   POS select
        barcode_type,  # F16  barcode number type
        '0',           # skip
        pos_flag,      # F47  POS flag
        f'"{barcode}"',# F92  barcode string
        '0',           # F91  origin country
        '0',           # skip
        '0',           # F89  free message 5
        '0',           # skip
        '0',           # F53  logo 1
        '0',           # F54  logo 2
        '0',           # skip
        '0',           # F61
        '0', '0', '0', '0', '0', '0',
    ]

    return (','.join(fields) + ',').encode('utf-8')


def format_delete_plu(plu_no: int) -> bytes:
    """Format a PLU delete record for MsgNo 2023. Payload: '{plu_no},'"""
    return f"{plu_no},".encode('utf-8')

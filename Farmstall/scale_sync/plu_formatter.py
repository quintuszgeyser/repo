"""
PLU data formatting and product filtering for BC-4000 scale sync.

MsgNo 1040: price-change only — 2-field CSV (kept for future rapid-update use)
MsgNo 1001: full PLU send — 63-field CSV with embedded Ishida description control codes

Field sequence derived from decompiling SLP-V SlpDbServer.dll
SerializeScaleDataAc4000(), South Africa path (IsLongPluBc4000Country=True).
"""
import logging
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

logger = logging.getLogger('plu_formatter')

MSG_NO_PRICE_CHANGE = 1040
MSG_NO_FULL_PLU = 1001

MAX_PLU_ID = 99_999


def should_sync(product: dict) -> bool:
    """
    Return True if this product should be pushed to the scale.

    Rejects:
    - Archived products
    - Products not for sale
    - Recipe products (assembled on POS, not scale items)
    - Products with no valid price
    - Products with id > 99999 (BC-4000 PLU limit)
    """
    if product.get('is_archived'):
        logger.debug(f"Skip {product['id']}: archived")
        return False

    if not product.get('is_for_sale'):
        logger.debug(f"Skip {product['id']}: not for sale")
        return False

    if product.get('product_type') == 'recipe':
        logger.debug(f"Skip {product['id']}: recipe type")
        return False

    if product['id'] > MAX_PLU_ID:
        logger.warning(f"Skip {product['id']}: exceeds BC-4000 PLU limit ({MAX_PLU_ID})")
        return False

    if product.get('sold_by_weight'):
        ppu = product.get('price_per_unit')
        if not ppu or Decimal(str(ppu)) <= 0:
            logger.debug(f"Skip {product['id']}: sold_by_weight but no valid price_per_unit")
            return False
    else:
        p = product.get('price')
        if not p or Decimal(str(p)) <= 0:
            logger.debug(f"Skip {product['id']}: no valid price")
            return False

    return True


def price_cents(product: dict) -> int:
    """
    Return the scale price in whole cents.

    - Fixed price items: price in Rand → cents (R24.90 → 2490)
    - Weight items: price_per_unit is R/g, scale shows /kg
      (R0.45/g × 100000 = 45000 cents/kg = R450/kg)

    Uses Decimal arithmetic to avoid float rounding bugs.
    """
    if product.get('sold_by_weight'):
        ppu = Decimal(str(product['price_per_unit']))
        return int((ppu * Decimal('100000')).quantize(
            Decimal('1'), rounding=ROUND_HALF_UP
        ))
    else:
        p = Decimal(str(product['price']))
        return int((p * Decimal('100')).quantize(
            Decimal('1'), rounding=ROUND_HALF_UP
        ))


MAX_NAME_CHARS = 20


def format_full_plu(product: dict) -> Optional[bytes]:
    """
    Format a product as MsgNo 1001 CSV (full PLU with name and price).

    Field sequence: 63 comma-separated fields matching SerializeScaleDataAc4000()
    South Africa BC-4000 path. Each field is {value}, or "{text}",

    Description (Field 94) uses Ishida control codes for 2-line label:
      \\x0d\\x0a = line feed + large font  → product name
      \\x0d\\x01 = line feed + small font  → "PER KG" or "EACH"

    Returns UTF-8 bytes, or None if formatting fails.
    """
    try:
        plu_id     = product['id']
        sales_mode = 0 if product.get('sold_by_weight') else 1
        price      = price_cents(product)
        name       = product.get('name', '')[:MAX_NAME_CHARS].upper().replace('"', '""')
        unit_line  = 'PER KG' if product.get('sold_by_weight') else 'EACH'
        # Ishida 2-line description: \x0d\xNN = newline + font code
        desc       = f'\x0d\x0a{name}\x0d\x01{unit_line}'
        price_s    = str(price)

        fields = [
            str(plu_id),   # F0   PLU number
            '0',           # F67  item code (0 = use PLU no)
            '0',           # DateFlag (0 = no date display)
            '0',           # F5   time flag
            '0',           # skip
            '0',           # F46  pack time offset
            '0',           # skip
            '0',           # F8   expiry time flag
            '0',           # skip
            '0',           # num3 date flag part 3
            '0',           # F45  expiry hours (0 because F8 < 2)
            '0',           # num2 date flag part 2
            '0',           # num4 date flag part 4
            '0', '0', '0', '0',              # skip×4
            '0',           # F59  label format 1 (0 = default)
            '0',           # F60  label format 2
            '0', '0', '0', '0',              # skip×4
            '0',           # F71  dept code
            '0',           # F72  group code
            '0', '0', '0',                   # skip×3
            '0',           # ExMsg1
            '0',           # ExMsg2
            '0',           # ExMsg3
            '0',           # Coupon
            '0', '0',                        # skip×2
            '0',           # skip
            '0',           # F65  cost price
            '0',           # F117 tax rate ×100 (SA; 0 = no override)
            '0', '0', '0', '0', '0',         # skip×5
            '0',           # skip F10 (BC4000 non-USA path)
            '0', '0',                        # skip×2
            '0',           # F7   open price flag
            '0',           # skip (nutrition not enabled)
            '0',           # skip F55 (BC4000 non-USA)
            '0',           # skip F9  (non-USA)
            f'"{desc}"',   # F94  *** DESCRIPTION — name + unit ***
            str(sales_mode),  # F2  sales mode (0=weight, 1=fixed)
            price_s,       # F62  price in cents
            price_s,       # F62  price in cents (required duplicate)
            '0',           # F3   markdown flag
            '0',           # F66  markdown price
            '0',           # skip
            '0',           # F42  pack quantity
            '0',           # F17  unit type
            '0',           # F64  fixed weight grams (0 for weighed)
            '0',           # F69  upper weight limit
            '0',           # F70  lower weight limit
            '0',           # F43  tare weight
            '0', '0', '0', '0',              # skip×4
            '0',           # F6   POS select
            '0',           # F16  barcode number type
            '0',           # skip
            '0',           # F47  POS flag
            '""',          # F92  barcode string (empty)
            '0',           # F91  origin country
            '0',           # skip
            '0',           # F89  free message 5
            '0',           # skip
            '0',           # F53  logo 1
            '0',           # F54  logo 2
            '0',           # skip
            '0',           # F61  (non-Australia path)
            '0', '0', '0', '0', '0', '0',   # skip×6 (non-NZ/USA/Taiwan)
        ]

        csv = ','.join(fields) + ','
        return csv.encode('utf-8')

    except Exception as e:
        logger.error(f"Failed to format full PLU {product['id']}: {e}")
        return None


def format_price_change(product: dict) -> Optional[bytes]:
    """
    Format a product as MsgNo 1040 CSV (price change only).

    CSV: "{plu_id},{price_cents},"
    e.g. "5,2490,"  → PLU 5, R24.90 fixed price
    e.g. "3,45000," → PLU 3, R450.00/kg weighed item

    Returns UTF-8 bytes, or None if price cannot be computed.
    """
    try:
        cents = price_cents(product)
        csv = f"{product['id']},{cents},"
        return csv.encode('utf-8')
    except Exception as e:
        logger.error(f"Failed to format PLU {product['id']}: {e}")
        return None

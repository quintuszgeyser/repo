"""
PLU data formatting and product filtering for BC-4000 scale sync.

Phase 1: MsgNo 1040 (price-change only) — 2-field CSV: PLU_NO,PRICE_CENTS,
Phase 2 (future): MsgNo 1001 (full PLU with name) — multi-field CSV
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

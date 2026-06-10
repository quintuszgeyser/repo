"""Unit tests for BC-4000 protocol encoding — no network required."""
import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from bc4000_client import num2bcd, bcd2num, num2nl, num2ns, nl2num, ns2num
from plu_formatter import price_cents, format_price_change, format_full_plu, should_sync


class TestBcdEncoding(unittest.TestCase):

    def test_num2bcd_basic(self):
        self.assertEqual(num2bcd(1001, 4), b'\x10\x01')
        self.assertEqual(num2bcd(1234, 4), b'\x12\x34')
        self.assertEqual(num2bcd(99, 4),   b'\x00\x99')
        self.assertEqual(num2bcd(0, 4),    b'\x00\x00')
        self.assertEqual(num2bcd(1040, 4), b'\x10\x40')

    def test_bcd2num_roundtrip(self):
        for v in [0, 1, 99, 100, 1001, 1040, 9999]:
            encoded = num2bcd(v, 4)
            decoded, offset = bcd2num(encoded, 0, 4)
            self.assertEqual(decoded, v, f"Roundtrip failed for {v}")
            self.assertEqual(offset, 2)

    def test_num2nl_roundtrip(self):
        for v in [0, 8, 100, 65535, 16777216]:
            encoded = num2nl(v)
            self.assertEqual(len(encoded), 4)
            decoded, _ = nl2num(encoded, 0)
            self.assertEqual(decoded, v)

    def test_num2ns_roundtrip(self):
        for v in [0, 1, 256, 65535]:
            encoded = num2ns(v)
            self.assertEqual(len(encoded), 2)
            decoded, _ = ns2num(encoded, 0)
            self.assertEqual(decoded, v)


class TestPriceConversion(unittest.TestCase):

    def test_fixed_price_cents(self):
        p = {'sold_by_weight': False, 'price': Decimal('24.90'), 'id': 1,
             'is_archived': False, 'is_for_sale': True, 'product_type': 'simple',
             'price_per_unit': None}
        self.assertEqual(price_cents(p), 2490)

    def test_fixed_price_float_input(self):
        # Float input must not produce rounding error
        p = {'sold_by_weight': False, 'price': 24.90, 'id': 1,
             'is_archived': False, 'is_for_sale': True, 'product_type': 'simple',
             'price_per_unit': None}
        self.assertEqual(price_cents(p), 2490)

    def test_fixed_price_zero_cents(self):
        p = {'sold_by_weight': False, 'price': Decimal('10.00'), 'id': 1,
             'is_archived': False, 'is_for_sale': True, 'product_type': 'simple',
             'price_per_unit': None}
        self.assertEqual(price_cents(p), 1000)

    def test_weight_price_per_kg(self):
        # R0.45/g = R450/kg = 45000 cents/kg
        p = {'sold_by_weight': True, 'price_per_unit': Decimal('0.45'), 'id': 2,
             'is_archived': False, 'is_for_sale': True, 'product_type': 'stock_item',
             'price': None}
        self.assertEqual(price_cents(p), 45000)

    def test_weight_price_rounding(self):
        # Ensure Decimal rounding, not float truncation
        p = {'sold_by_weight': True, 'price_per_unit': 0.001, 'id': 3,
             'is_archived': False, 'is_for_sale': True, 'product_type': 'stock_item',
             'price': None}
        result = price_cents(p)
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)


class TestProductFilter(unittest.TestCase):

    def _base(self, **overrides):
        p = {
            'id': 1, 'name': 'Test', 'price': Decimal('10.00'),
            'price_per_unit': None, 'sold_by_weight': False,
            'is_archived': False, 'is_for_sale': True, 'product_type': 'simple',
        }
        p.update(overrides)
        return p

    def test_valid_product(self):
        self.assertTrue(should_sync(self._base()))

    def test_archived(self):
        self.assertFalse(should_sync(self._base(is_archived=True)))

    def test_not_for_sale(self):
        self.assertFalse(should_sync(self._base(is_for_sale=False)))

    def test_recipe(self):
        self.assertFalse(should_sync(self._base(product_type='recipe')))

    def test_id_over_limit(self):
        self.assertFalse(should_sync(self._base(id=100_000)))

    def test_no_price(self):
        self.assertFalse(should_sync(self._base(price=None)))

    def test_zero_price(self):
        self.assertFalse(should_sync(self._base(price=0)))

    def test_weight_no_ppu(self):
        self.assertFalse(should_sync(self._base(sold_by_weight=True, price_per_unit=None)))

    def test_weight_zero_ppu(self):
        self.assertFalse(should_sync(self._base(sold_by_weight=True, price_per_unit=0)))


class TestFormatPriceChange(unittest.TestCase):

    def test_fixed_price(self):
        p = {'id': 1, 'price': Decimal('24.90'), 'sold_by_weight': False,
             'price_per_unit': None, 'is_archived': False, 'is_for_sale': True,
             'product_type': 'simple'}
        result = format_price_change(p)
        self.assertEqual(result, b'1,2490,')

    def test_weight_item(self):
        p = {'id': 3, 'price': None, 'sold_by_weight': True,
             'price_per_unit': Decimal('0.45'), 'is_archived': False,
             'is_for_sale': True, 'product_type': 'stock_item'}
        result = format_price_change(p)
        self.assertEqual(result, b'3,45000,')

    def test_returns_bytes(self):
        p = {'id': 5, 'price': Decimal('9.99'), 'sold_by_weight': False,
             'price_per_unit': None, 'is_archived': False, 'is_for_sale': True,
             'product_type': 'simple'}
        result = format_price_change(p)
        self.assertIsInstance(result, bytes)


class TestFullPluFormat(unittest.TestCase):
    """Tests for MsgNo 1001 full PLU formatter."""

    def _weight(self, **overrides):
        p = {'id': 3, 'name': 'Biltong', 'price': None,
             'price_per_unit': Decimal('0.45'), 'sold_by_weight': True,
             'is_archived': False, 'is_for_sale': True, 'product_type': 'stock_item'}
        p.update(overrides)
        return p

    def _fixed(self, **overrides):
        p = {'id': 10, 'name': 'Bread Roll', 'price': Decimal('12.50'),
             'price_per_unit': None, 'sold_by_weight': False,
             'is_archived': False, 'is_for_sale': True, 'product_type': 'simple'}
        p.update(overrides)
        return p

    def _parse(self, product):
        """Return CSV fields as list (strips trailing empty field from trailing comma)."""
        raw = format_full_plu(product).decode('utf-8')
        # Split carefully — quoted fields may contain commas (they don't here, but be safe)
        # Simple split is fine since we control the format
        fields = raw.rstrip(',').split(',')
        return fields

    def test_returns_bytes(self):
        self.assertIsInstance(format_full_plu(self._weight()), bytes)

    def test_field_count_weight(self):
        fields = self._parse(self._weight())
        # 85 value positions matching SerializeScaleDataAc4000 South Africa call count
        raw = format_full_plu(self._weight()).decode('utf-8')
        self.assertEqual(raw.count(','), 85,
                         f"Expected 85 commas in full PLU CSV, got {raw.count(',')}")

    def test_field_count_fixed(self):
        raw = format_full_plu(self._fixed()).decode('utf-8')
        self.assertEqual(raw.count(','), 85)

    def test_plu_id_first_field(self):
        fields = self._parse(self._weight())
        self.assertEqual(fields[0], '3')

    def test_description_weight_item(self):
        raw = format_full_plu(self._weight()).decode('utf-8')
        self.assertIn('\x0d\x0aBILTONG\x0d\x01PER KG', raw)

    def test_description_fixed_item(self):
        raw = format_full_plu(self._fixed()).decode('utf-8')
        self.assertIn('\x0d\x0aBREAD ROLL\x0d\x01EACH', raw)

    def test_name_uppercase(self):
        raw = format_full_plu(self._fixed(name='bread roll')).decode('utf-8')
        self.assertIn('BREAD ROLL', raw)
        self.assertNotIn('bread roll', raw)

    def test_name_truncated_at_20_chars(self):
        long_name = 'A' * 25
        raw = format_full_plu(self._fixed(name=long_name)).decode('utf-8')
        # Only 20 A's should appear in the description
        self.assertIn('A' * 20, raw)
        self.assertNotIn('A' * 21, raw)

    def test_sales_mode_weight(self):
        # sales_mode field is at a fixed position — find it after the description
        # It comes right after the closing quote of the description
        raw = format_full_plu(self._weight()).decode('utf-8')
        # Find the description end and check next field
        desc_end = raw.index('",')  # closing quote of description
        after_desc = raw[desc_end + 2:].split(',')
        self.assertEqual(after_desc[0], '0')   # sales_mode = 0 (weight)

    def test_sales_mode_fixed(self):
        raw = format_full_plu(self._fixed()).decode('utf-8')
        desc_end = raw.index('",')
        after_desc = raw[desc_end + 2:].split(',')
        self.assertEqual(after_desc[0], '1')   # sales_mode = 1 (fixed)

    def test_price_written_twice(self):
        # R450/kg → 45000 cents; should appear twice consecutively after sales_mode
        raw = format_full_plu(self._weight()).decode('utf-8')
        self.assertIn('45000,45000,', raw)

    def test_fixed_price_written_twice(self):
        # R12.50 → 1250 cents
        raw = format_full_plu(self._fixed()).decode('utf-8')
        self.assertIn('1250,1250,', raw)


if __name__ == '__main__':
    unittest.main(verbosity=2)

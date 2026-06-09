"""Unit tests for BC-4000 protocol encoding — no network required."""
import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from bc4000_client import num2bcd, bcd2num, num2nl, num2ns, nl2num, ns2num
from plu_formatter import price_cents, format_price_change, should_sync


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


if __name__ == '__main__':
    unittest.main(verbosity=2)

# -*- coding: utf-8 -*-
"""
Tests for account_payment_term_fixed_date.

Run with:
    odoo-bin -d <db> --test-enable -i account_payment_term_fixed_date
or:
    python -m pytest tests/test_formula.py   (pure-Python, no Odoo needed)
"""
import unittest
from datetime import date

# Import helper directly (no Odoo dependency needed for pure logic tests)
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from models.account_payment_term import _compute_fixed_date, _parse_month_formula


class TestParseMonthFormula(unittest.TestCase):

    def test_fixed_month(self):
        self.assertEqual(_parse_month_formula('1',  5), (1, 0))
        self.assertEqual(_parse_month_formula('6',  5), (6, 0))
        self.assertEqual(_parse_month_formula('12', 5), (12, 0))

    def test_fixed_month_out_of_range(self):
        with self.assertRaises(ValueError):
            _parse_month_formula('0', 5)
        with self.assertRaises(ValueError):
            _parse_month_formula('13', 5)

    def test_relative_plus(self):
        # month+5 from month 3 (March) → month 8 (August), year carry 0
        self.assertEqual(_parse_month_formula('month+5', 3), (8, 0))

    def test_relative_plus_year_rollover(self):
        # month+5 from month 10 (October) → 10+5=15 → month 3, +1 year
        self.assertEqual(_parse_month_formula('month+5', 10), (3, 1))

    def test_relative_minus(self):
        # month-1 from month 3 → month 2, 0 year carry
        self.assertEqual(_parse_month_formula('month-1', 3), (2, 0))

    def test_relative_minus_year_rollback(self):
        # month-2 from month 1 → -1 → month 11, -1 year
        self.assertEqual(_parse_month_formula('month-2', 1), (11, -1))

    def test_invalid(self):
        with self.assertRaises(ValueError):
            _parse_month_formula('banana', 5)


class TestComputeFixedDate(unittest.TestCase):

    # --- Caso 1: 31 de enero próximo ---
    def test_31_enero_before_january(self):
        # Invoice in August → next January 31
        inv = date(2024, 8, 15)
        result = _compute_fixed_date(inv, 31, '1')
        self.assertEqual(result, date(2025, 1, 31))

    def test_31_enero_exact_day(self):
        # Invoice ON January 31 → same day (not advanced)
        inv = date(2025, 1, 31)
        result = _compute_fixed_date(inv, 31, '1')
        self.assertEqual(result, date(2025, 1, 31))

    def test_31_enero_after_january(self):
        # Invoice in February → next January 31 is next year
        inv = date(2025, 2, 1)
        result = _compute_fixed_date(inv, 31, '1')
        self.assertEqual(result, date(2026, 1, 31))

    # --- Caso 2: 30 de junio próximo ---
    def test_30_junio_before(self):
        inv = date(2025, 1, 15)
        result = _compute_fixed_date(inv, 30, '6')
        self.assertEqual(result, date(2025, 6, 30))

    def test_30_junio_after(self):
        inv = date(2025, 7, 1)
        result = _compute_fixed_date(inv, 30, '6')
        self.assertEqual(result, date(2026, 6, 30))

    # --- Caso 3: month+5, día 31 ---
    def test_month_plus_5_from_august(self):
        # August + 5 = January next year, day 31
        inv = date(2024, 8, 1)
        result = _compute_fixed_date(inv, 31, 'month+5')
        self.assertEqual(result, date(2025, 1, 31))

    def test_month_plus_5_from_january(self):
        # January + 5 = June, day 30 (June has 30 days, 31 clamped to 30)
        inv = date(2025, 1, 1)
        result = _compute_fixed_date(inv, 31, 'month+5')
        self.assertEqual(result, date(2025, 6, 30))  # clamped

    def test_month_plus_2_day_15(self):
        inv = date(2025, 3, 10)
        result = _compute_fixed_date(inv, 15, 'month+2')
        self.assertEqual(result, date(2025, 5, 15))

    # --- Día clamping: febrero ---
    def test_day_clamped_february(self):
        # Fixed month=2 (February), day=31 → clamped to 28 (2025 non-leap)
        inv = date(2024, 3, 1)
        result = _compute_fixed_date(inv, 31, '2')
        self.assertEqual(result, date(2025, 2, 28))

    def test_day_clamped_february_leap(self):
        # 2024 is leap year; invoice in Jan 2024 → Feb 29, 2024
        inv = date(2024, 1, 1)
        result = _compute_fixed_date(inv, 31, '2')
        self.assertEqual(result, date(2024, 2, 29))

    # --- month+0: mismo mes, fecha futura ---
    def test_month_plus_zero_future_day(self):
        inv = date(2025, 5, 1)
        result = _compute_fixed_date(inv, 15, 'month+0')
        self.assertEqual(result, date(2025, 5, 15))

    def test_month_plus_zero_past_day(self):
        # Invoice on May 20, day=15 → same month already passed → June 15
        inv = date(2025, 5, 20)
        result = _compute_fixed_date(inv, 15, 'month+0')
        self.assertEqual(result, date(2025, 6, 15))


if __name__ == '__main__':
    unittest.main()

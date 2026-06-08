import pytest
from datetime import datetime
from dateutil.rrule import MONTHLY
from gazette.utils.dates import generate_dates_sequence, monthly_sequence, YearMonthDate

class TestMonthlySequenceEstrutural:

    def test_when_startday_doesnt_exist_monthly_should_still_return_consecutive_sequence_with_them(self):
        """Cover: Condition A (True - Within the interval) and Condition B (False - Day 31 does not exist in all)"""
        assert monthly_sequence(
            start=datetime(2022, 1, 31), end=datetime(2022, 12, 31)
        ) == [
            YearMonthDate(2022, 1), YearMonthDate(2022, 2), YearMonthDate(2022, 3),
            YearMonthDate(2022, 4), YearMonthDate(2022, 5), YearMonthDate(2022, 6),
            YearMonthDate(2022, 7), YearMonthDate(2022, 8), YearMonthDate(2022, 9),
            YearMonthDate(2022, 10), YearMonthDate(2022, 11), YearMonthDate(2022, 12),
        ]

    def test_monthly_sequence_happy_path_all_days_exist(self):
        """Cover: Condition A (True) and Condition B (True) -> All months contain the day (e.g., Day 1)"""
        assert monthly_sequence(
            start=datetime(2022, 1, 1), end=datetime(2022, 3, 1)
        ) == [
            YearMonthDate(2022, 1),
            YearMonthDate(2022, 2),
            YearMonthDate(2022, 3),
        ]

    def test_monthly_boundary_day_30_fevereiro_exception(self):
        """Evaluate the boundary behavior when the 30th does not exist in February, but does exist in other months."""
        assert monthly_sequence(
            start=datetime(2022, 1, 30), end=datetime(2022, 3, 30)
        ) == [
            YearMonthDate(2022, 1),
            YearMonthDate(2022, 2), # Fevereiro corrigido internamente
            YearMonthDate(2022, 3),
        ]

    def test_monthly_boundary_day_28_safe_path(self):
        """Evaluate the safe boundary where the day exists mathematically in all Gregorian iterations."""
        assert monthly_sequence(
            start=datetime(2022, 1, 28), end=datetime(2022, 3, 28)
        ) == [
            YearMonthDate(2022, 1),
            YearMonthDate(2022, 2),
            YearMonthDate(2022, 3),
        ]
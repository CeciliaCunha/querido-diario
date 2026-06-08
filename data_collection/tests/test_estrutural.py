import pytest
from datetime import datetime
from dateutil.rrule import DAILY, YEARLY
from gazette.utils.dates import generate_dates_sequence

class TestGenerateDatesSequenceMCDC:
    def test_when_end_is_included_and_start_and_end_are_equal_should_return_both(self):
        """Covers the duplication decision: Decision 1 (True) and Decision 2 (True)"""
        result = generate_dates_sequence(
            start=datetime(2025, 5, 5),
            end=datetime(2025, 5, 5),
            recurrence=DAILY,
            end_included=True
        )
        assert result == [datetime(2025, 5, 5), datetime(2025, 5, 5)]

    def test_mcdc_condition_b_false(self):
        """Copper: Decision 1 (True) and Decision 2 (False) -> Output with a single element"""
        result = generate_dates_sequence(
            start=datetime(2025, 5, 5),
            end=datetime(2025, 5, 5),
            recurrence=DAILY,
            end_included=False
        )
        assert result == [datetime(2025, 5, 5)]

    def test_mcdc_condition_a_false_and_boundary_plus_one(self):
        """Copper: Decision 1 (False) and Decision 2 (True) -> Regular sequence generated"""
        result = generate_dates_sequence(
            start=datetime(2025, 5, 5),
            end=datetime(2025, 5, 6),
            recurrence=DAILY,
            end_included=True
        )
        assert result == [datetime(2025, 5, 5), datetime(2025, 5, 6)]

    def test_boundary_minus_one_day(self):
        """Evaluates behavior when the start date exceeds the end date (Invalid)"""
        result = generate_dates_sequence(
            start=datetime(2025, 5, 6),
            end=datetime(2025, 5, 5),
            recurrence=DAILY,
            end_included=True
        )
        assert result == []
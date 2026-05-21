import pytest
from datetime import date, datetime
from scrapy.exceptions import NotConfigured


def make_spider_class(**class_attrs):
    from gazette.spiders.base import BaseGazetteSpider

    attrs = {
        "name": "test_spider",
        "start_urls": ["http://example.com"],
        **class_attrs,
    }
    return type("TestSpider", (BaseGazetteSpider,), attrs)


def make_complete_spider_class():
    return make_spider_class(
        TERRITORY_ID="1234567",
        allowed_domains=["example.com"],
        start_date=date(2020, 1, 1),
    )


class TestMissingRequiredAttributes:

    def test_when_territory_id_is_missing_should_raise_not_configured(self):
        SpiderClass = make_spider_class(
            allowed_domains=["example.com"],
            start_date=date(2020, 1, 1),
        )
        with pytest.raises(NotConfigured):
            SpiderClass()

    def test_when_allowed_domains_is_missing_should_raise_not_configured(self):
        SpiderClass = make_spider_class(
            TERRITORY_ID="1234567",
            start_date=date(2020, 1, 1),
        )
        with pytest.raises(NotConfigured):
            SpiderClass()

    def test_when_start_date_is_missing_should_raise_not_configured(self):
        SpiderClass = make_spider_class(
            TERRITORY_ID="1234567",
            allowed_domains=["example.com"],
        )
        with pytest.raises(NotConfigured):
            SpiderClass()

    def test_when_all_required_attributes_are_present_should_not_raise(self):
        SpiderClass = make_complete_spider_class()
        assert SpiderClass() is not None


class TestDefaultBehaviorWhenStartAndEndAreOmitted:

    def test_when_start_is_none_should_keep_class_start_date(self):
        SpiderClass = make_complete_spider_class()
        spider = SpiderClass(start=None, end=None)
        assert spider.start_date == date(2020, 1, 1)

    def test_when_end_is_none_should_set_end_date_to_today(self):
        SpiderClass = make_complete_spider_class()
        spider = SpiderClass(start=None, end=None)
        assert spider.end_date == datetime.today().date()


class TestValidStartAndEnd:

    def test_when_start_and_end_are_valid_should_convert_both_correctly(self):
        SpiderClass = make_complete_spider_class()
        spider = SpiderClass(start="2024-06-15", end="2024-12-31")
        assert spider.start_date == date(2024, 6, 15)
        assert spider.end_date == date(2024, 12, 31)

    def test_when_start_is_first_day_of_year_should_convert_correctly(self):
        SpiderClass = make_complete_spider_class()
        spider = SpiderClass(start="2024-01-01")
        assert spider.start_date == date(2024, 1, 1)

    def test_when_start_is_last_day_of_year_should_convert_correctly(self):
        SpiderClass = make_complete_spider_class()
        spider = SpiderClass(start="2024-12-31")
        assert spider.start_date == date(2024, 12, 31)

    def test_when_start_is_feb_29_on_leap_year_should_convert_correctly(self):
        SpiderClass = make_complete_spider_class()
        spider = SpiderClass(start="2024-02-29")
        assert spider.start_date == date(2024, 2, 29)


class TestInvalidStart:

    def test_when_start_has_wrong_format_should_raise_value_error(self):
        SpiderClass = make_complete_spider_class()
        with pytest.raises(ValueError):
            SpiderClass(start="15/06/2024")

    def test_when_start_has_nonexistent_month_should_raise_value_error(self):
        SpiderClass = make_complete_spider_class()
        with pytest.raises(ValueError):
            SpiderClass(start="2024-13-01")

    def test_when_start_is_feb_29_on_non_leap_year_should_raise_value_error(self):
        SpiderClass = make_complete_spider_class()
        with pytest.raises(ValueError):
            SpiderClass(start="2023-02-29")


class TestInvalidEnd:

    def test_when_end_has_wrong_format_should_raise_value_error(self):
        SpiderClass = make_complete_spider_class()
        with pytest.raises(ValueError):
            SpiderClass(start="2024-06-15", end="30/06/2024")

    def test_when_end_has_nonexistent_day_should_raise_value_error(self):
        SpiderClass = make_complete_spider_class()
        with pytest.raises(ValueError):
            SpiderClass(start="2024-06-15", end="2024-01-32")
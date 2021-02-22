import pytest
from lib.website_checker_bot import WebsiteCheckerBot


@pytest.fixture
def fixture_website_checker_bot(fixture_website_record):
    return WebsiteCheckerBot(fixture_website_record)


def test_check_content_regex(fixture_website_checker_bot, fixture_website_record, requests_mock):
    # Success regex and status_code
    requests_mock.get(fixture_website_record.url, text="<h1>Hello</h1>", status_code=200)

    website_checker_record = fixture_website_checker_bot.run_test()
    assert website_checker_record.is_regex_pattern_valid is True
    assert website_checker_record.is_status_code_valid is True

    # Failed regex and status_code
    requests_mock.get(fixture_website_record.url, text="I don't have any h1", status_code=301)

    website_checker_record = fixture_website_checker_bot.run_test()
    assert website_checker_record.is_regex_pattern_valid is False
    assert website_checker_record.is_status_code_valid is False

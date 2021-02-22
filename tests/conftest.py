import faust
import pytest
from tasks.models import WebsiteCheckerRecord, WebsiteRecord


@pytest.fixture()
def fixture_app(event_loop):
    app = faust.App("test-example")
    app.finalize()
    app.conf.store = "memory://"
    app.flow_control.resume()
    return app


@pytest.fixture
def fixture_website_record():
    return WebsiteRecord(
        id="1",
        website_id=1,
        url="http://httpbin.org/html",
        regex_pattern=r"<h1>(?:.*)</h1>",
    )


@pytest.fixture
def fixture_website_checker_record():
    return WebsiteCheckerRecord(
        id="id",
        website_id=1,
        is_status_code_valid=True,
        is_regex_pattern_valid=False,
        response_time=0,
    )

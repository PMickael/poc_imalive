# coding: utf-8
try:
    # Use re2 (faster) or lib regex instead of re in production
    # Because it can stuck(infinity backtracking) with some specific regex patterns
    import re2 as re
except Exception:
    import re

import logging
import traceback

import faust
import requests
import requests.exceptions
from tasks.models import WebsiteCheckerRecord, WebsiteRecord

ERROR_TIMEOUT = "Timeout"
ERROR_READ_TIMEOUT = "Read timeout"
ERROR_CONNECTION = "Connection error"
ERROR_TIMEOUT_EXEC = "Execution timeout"

logger = logging.getLogger(__name__)


class WebsiteCheckerBot(object):
    """WebsiteChecker - Tool to check website status // response_time // pattern"""

    DEFAULT_REQUESTS_HEADERS = {
        "user-agent": "WebsiteCheckerBot - v0.0.1",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "accept-encoding": "gzip, deflate",
        "connection": "close",
    }

    DEFAULT_REQUEST_CONFIG = {
        "timeout": 5,  # Define default timeout
        "allow_redirects": False,
    }

    def __init__(self, website_record: WebsiteRecord):
        # Use default headers (in case with need specific headers by website)
        self.request_headers = self.DEFAULT_REQUESTS_HEADERS.copy()
        self.request_configuration = self.DEFAULT_REQUEST_CONFIG.copy()

        # Load instance variable
        self.website_id = website_record.website_id
        self.url = website_record.url
        self.regex_pattern = website_record.regex_pattern

        self.event_data = {
            "event": "website_checker",
            "website_id": self.website_id,
            "url": self.url,
            "regex_pattern": self.regex_pattern,
        }

    def run_test(self) -> WebsiteCheckerRecord:
        try:
            request_response = self.do_get()

            if request_response is not False:
                # Execute sub checker tasks
                is_status_code_valid = self._check_status_code(request_response)
                is_regex_pattern_valid = self._check_content_regex(request_response)
                response_time = self._check_response_time(request_response)

            return WebsiteCheckerRecord(
                id=faust.uuid(),
                website_id=self.website_id,
                is_status_code_valid=is_status_code_valid,
                is_regex_pattern_valid=is_regex_pattern_valid,
                response_time=response_time,
            )

        except Exception as e:
            logger.critical(e)
            self.event_data["error_level"] = logging.CRITICAL
            self.event_data["error"] = str(traceback.format_exc())
            # TODO: Logging event_data into a separate process

            raise

    def _check_status_code(self, request_response: requests.Response) -> bool:
        # Add information in the event log
        self.event_data["status_code"] = request_response.status_code

        logger.debug("[WebsiteCheckerBot][StatusCode] %s" % request_response.status_code)

        # If the status code is valid for our purpose (is 30x OK ?)
        if request_response.status_code == 200:
            return True

        return False

    def _check_content_regex(self, request_response: requests.Response) -> bool:
        # Check if regex pattern exists
        if self.regex_pattern:
            # Maybe the regex is invalid (user managed)
            try:
                logger.debug("[WebsiteCheckerBot][ContentRegex] %s" % self.regex_pattern)
                if re.search(self.regex_pattern, request_response.text):
                    return True
            except Exception:
                self.event_data["error"]["regex"] = "invalid_regex"

            return False

        # Do not have any regex_checker defined
        return None

    def _check_response_time(self, request_response: requests.Response) -> float:
        return request_response.elapsed.total_seconds()

    def do_get(self):
        try:
            request_response = requests.get(self.url, headers=self.request_headers, **self.request_configuration)
            logger.debug("[WebsiteCheckerBot][Headers] %s" % request_response.headers)

            return request_response
        except requests.exceptions.ConnectTimeout:
            self.event_data["error_level"] = logging.WARNING
            self.event_data["error"] = ERROR_TIMEOUT
        except requests.exceptions.ReadTimeout:
            self.event_data["error_level"] = logging.WARNING
            self.event_data["error"] = ERROR_READ_TIMEOUT
        except requests.exceptions.ConnectionError:
            self.event_data["error_level"] = logging.WARNING
            self.event_data["error"] = ERROR_CONNECTION

        return False

import faust


class WebsiteRecord(faust.Record):
    id: int
    website_id: int
    url: str
    regex_pattern: str = None


class WebsiteCheckerRecord(faust.Record, serializer="json"):
    id: int
    website_id: int
    is_status_code_valid: bool = False
    is_regex_pattern_valid: bool = False
    response_time: float = None

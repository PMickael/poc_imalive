from unittest.mock import Mock, patch

import pytest
from tasks.agents import agent_website_checker


@pytest.mark.asyncio()
async def test_agent_website_checker(
    fixture_website_record, fixture_website_checker_record, fixture_app, requests_mock
):
    requests_mock.get(fixture_website_record.url, text="<h1>Hello</h1>", status_code=200)

    with patch("tasks.agents.website_analytics_topic") as mocked_website_analytics_topic:
        mocked_website_analytics_topic.send = mocked_wat()
        async with agent_website_checker.test_context() as agent:
            event = await agent.put(fixture_website_record)
            assert event.value.id == fixture_website_record.id


def mocked_wat(return_value=None, **kwargs):
    """Mock tasks.agents.website_analytics_topic do really send task."""

    async def wrapped(*args, **kwargs):
        return return_value

    return Mock(wraps=wrapped, **kwargs)

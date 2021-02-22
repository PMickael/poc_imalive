from typing import List

import faust
from tasks.models import WebsiteCheckerRecord, WebsiteRecord


class WebsiteAnalytics(object):
    """
    Website analytics class, use for database related informations of websites
    """

    def __init__(self, pg_connection):
        self.pg_connection = pg_connection

    async def followed_websites(self) -> List:
        """
        Load all websites followed by the system

        :returns:   List of faust WebsiteRecord
        :rtype:     List[WebsiteRecord]
        """
        rows = await self.pg_connection.fetch(
            "SELECT id as website_id, url, regex_pattern FROM website WHERE status = 1"
        )

        followed_websites_list = []
        for row in rows:
            # Convert asyncpg.Record to a seralized version
            serialized = dict(zip(row.keys(), row.values()))
            # Add the faust generated id
            # Or use a specific one like region worker, to be handle by the right worker with group_by
            serialized["id"] = faust.uuid()

            followed_websites_list.append(WebsiteRecord.loads(serialized))

        return followed_websites_list

    async def persist(self, website_checker_record: WebsiteCheckerRecord) -> None:
        """
        Persist Website Analytics

        :param      website_checker_record:  The website checker record
        :type       website_checker_record:  WebsiteCheckerRecord

        """
        await self.pg_connection.execute(
            """
            INSERT INTO "website_analytics" (
                website_id, is_status_code_valid, is_regex_pattern_valid, response_time, created_at
            ) VALUES (
                $1, $2, $3, $4, NOW()
            )
            """,
            website_checker_record.website_id,
            website_checker_record.is_status_code_valid,
            website_checker_record.is_regex_pattern_valid,
            website_checker_record.response_time,
        )

    async def resume(self):
        """
        DateHistogram every hour statistics

        :returns:   List of query row
        :rtype:     List[asyncpg.Record]
        """
        cursor = await self.pg_connection.fetch(
            """
            SELECT
                website_id,
                date_trunc('hour', created_at) as hour_interval,
                count(is_status_code_valid = true) as is_status_code_valid_count,
                count(*) as total_checked,
                count(is_regex_pattern_valid = true) as is_regex_pattern_valid_count,
                AVG(response_time) as avg_response_time
            FROM "website_analytics"
            GROUP BY website_id, hour_interval
            ORDER BY website_id, hour_interval;
        """
        )

        rows = cursor.fetchall()
        for row in rows:
            yield row

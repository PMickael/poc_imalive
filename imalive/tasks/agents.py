import logging

from app import app
from lib.website_analytics import WebsiteAnalytics
from lib.website_checker_bot import WebsiteCheckerBot

from .models import WebsiteCheckerRecord, WebsiteRecord

website_checker_topic = app.topic("website_checker", value_type=WebsiteRecord)
website_analytics_topic = app.topic("website_analytics", value_type=WebsiteCheckerRecord)

logger = logging.getLogger(__name__)


@app.agent(website_checker_topic)
async def agent_website_checker(events):
    async for website_record in events:
        logger.info(f"Event received. Website URL {website_record.url}")

        # Load the WebsiteCheckerBot library and run all test
        website_checker = WebsiteCheckerBot(website_record)

        # Return website_checker test result faust record
        website_checker_record = website_checker.run_test()
        logger.info(website_checker_record)
        await website_analytics_topic.send(value=website_checker_record)

        yield website_record


@app.agent(website_analytics_topic)
async def agent_website_analytics(events):
    async for website_checker_record in events:
        logger.info(f"Event received. Website Id {website_checker_record.website_id}")

        db_pool = await app.db_pool()

        # Acquire a connection into the postgresql pool to persist data into postgre
        async with db_pool.acquire() as pg_connection:
            try:
                website_analytics = WebsiteAnalytics(pg_connection)
                await website_analytics.persist(website_checker_record)

            # catch any exception and display a log
            # we should probably be more precise on the exception
            # and forward this exception to distributed logging system
            except Exception:
                logger.exception("Error while inserting in DB, continuing....")
            finally:
                logger.info(website_checker_record)


@app.timer(interval=10.0)
async def producer_website_checker():
    db_pool = await app.db_pool()
    async with db_pool.acquire() as pg_connection:

        # We generated task for all website followed
        website_analytics = WebsiteAnalytics(pg_connection)
        list_website_record = await website_analytics.followed_websites()

        for website_record in list_website_record:
            # Start the website_checker task
            await website_checker_topic.send(value=website_record)

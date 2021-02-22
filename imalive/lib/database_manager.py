import asyncio

import asyncpg
from asyncpg.pool import Pool
from simple_settings import settings


# add faust_loop to prevent error on ssl transport
async def db_pool(faust_loop: asyncio.AbstractEventLoop = None) -> Pool:
    return await asyncpg.create_pool(dsn=settings.POSTGRE_DSN, loop=faust_loop)


async def db_bootstrap() -> None:
    pg_pool = await db_pool()

    async with pg_pool.acquire() as pg_connection:
        # Create website table with fake website checking tasks
        await pg_connection.execute(
            """
            CREATE TABLE IF NOT EXISTS "website" (
               "id" serial NOT NULL,
               "url" character varying(2048) NOT NULL,
               "created_at" timestamp NOT NULL,
               "regex_pattern" text NULL,
               "status" smallint NOT NULL DEFAULT '1',
               CONSTRAINT "website_id" PRIMARY KEY ("id")
            );
            INSERT INTO "website" (id, url, created_at, regex_pattern, status)
            VALUES
                (1, 'https://httpbin.org/html', NOW(), '<h1>(?:.*)</h1>', 1),
                (2, 'https://httpbin.org/html', NOW(), '<h2>(?:.*)</h2>', 1),
                (3, 'https://httpbin.org/html', NOW(), '<h3>(?:.*)</h3>', 1),
                (4, 'https://httpbin.org/html', NOW(), '<p>\s(?:Availing himself of the mild)', 1)
            ON CONFLICT (id) DO NOTHING;
            """  # noqa: W605
        )

        # Create website_analytics table to store checker response
        await pg_connection.execute(
            """
            SET timezone TO 'UTC';
            CREATE TABLE IF NOT EXISTS "website_analytics" (
                "website_id" integer NOT NULL,
                "created_at" timestamp NOT NULL,
                "is_status_code_valid" boolean NOT NULL,
                "is_regex_pattern_valid" boolean,
                "response_time" real,
                CONSTRAINT "website_analytics_website_id_created_at" PRIMARY KEY ("website_id", "created_at")
            );
            """,
        )

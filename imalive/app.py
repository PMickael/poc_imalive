import logging
from typing import Dict, List

import faust
from asyncpg.pool import Pool
from lib.database_manager import db_bootstrap, db_pool
from simple_settings import settings


# https://stackoverflow.com/questions/56252406/how-to-work-with-asyncpg-connection-pool-in-faust-agent
#
# Extend faust.App to handle pg pooling
#
class ImaliveApp(faust.App):
    def __init__(self, *args: List, **kwargs: Dict) -> None:
        self._db_pool = None
        super().__init__(*args, **kwargs)

    async def on_start(self) -> None:
        # For testing purpose automatically create the database
        await db_bootstrap()
        await super().on_start()

    async def db_pool(self) -> Pool:
        if not self._db_pool:
            logging.warning("imalive.db_pool initialization...")
            self._db_pool = await db_pool()
            logging.warning("imalive.db_pool initialization...done ✓")

        return self._db_pool

    async def on_stop(self) -> None:
        logging.warning("imalive.db_pool terminate")
        db_pool = await self.db_pool()
        db_pool.terminate()
        await super().on_stop()


app = ImaliveApp(
    id=1,
    debug=settings.DEBUG,
    autodiscover=["tasks"],
    broker=settings.KAFKA_BOOTSTRAP_SERVER,
    store=settings.STORE_URI,
    logging_config=settings.LOGGING,
    topic_allow_declare=settings.TOPIC_ALLOW_DECLARE,
    topic_disable_leader=settings.TOPIC_DISABLE_LEADER,
    broker_credentials=settings.SSL_CONTEXT,
)

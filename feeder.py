from core.config import (
    MAIN_DB_CONN_STRING,
    FEED_JOBS_QUEUE_NAME,
    FEEDER_IDLE_SLEEP_INTERVAL,
    FEEDER_ERROR_SLEEP_INTERVAL,
)

from core.database.database import get_db
from core.database.crud.feeds import (
    read_next_overdue_active_feed,
    update_feed_status,
    update_feed_refresh_complete,
    read_overdue_active_feeds,
)
from core.enums.statuses import BottifyStatus
from core.elasticsearch.utils import bulk_index
from core.database.crud.config_key import read_config_key_by_name
from core.worker import bottify_worker
from pydantic import BaseModel
import boto3
import asyncio

# DEPRECATED
class FeederConfigModel(BaseModel):
    interval_seconds: int = 60


class Feeder:
    def __init__(self):
        self.database = get_db()
        self.started = False
        self.loop = asyncio.get_event_loop()
        self.config_key_name = "FeederConfig"
        self.configs = None

    async def start(self):
        if not self.database:
            print("FeedManager Failed to Start:Database Connection String Not Provided")
            return self
        await self.database.connect()
        config_data = await read_config_key_by_name(database, self.config_key_name)
        if not config_data:
            logging.error("Start : Failed to Read Feeder Config Key from Database")
            return self
        try:
            self.configs = FeederConfigModel.parse_raw(config_data.value)
            self.started = True
        except ValidationError as ve:
            logging.error(f"Start : FeederConfigModel : ValidationError : {ve.json()}")
        return self

    async def run(self):
        await self.start()
        if not self.started:
            logging.error("Run : Startup Failed")
            return
        update_interval_seconds = self.configs.interval_seconds
        if not update_interval_seconds:
            logging.error("Run : Failed to Load Required Update Interval from Configs")
            return
        while True:
            overdue_feeds = await read_overdue_active_feeds(self.database)
            if not overdue_feeds:
                logging.info(
                    f"Run : No Overdue Feeds : Sleeping for {self.configs.inverval_seconds}s"
                )
            else:
                for feed in overdue_feeds:
                    params = {"feed_id": feed.id}
                    bottify_worker.send_task(
                        "core.worker.refresh_feed", kwargs=params, queue="feed_tasks"
                    )
                    logging.info(f"Run : Update Started : Feed ID {feed.id}")
            await asyncio.sleep(update_interval_seconds)

    def DoWork(self):
        if not self.started:
            self.loop.run_until_complete(self.start())
        if not self.started:
            print("Feeder Failed to Start")
            return
        self.loop.run_until_complete(self.update_feeds())


def main():
    feeder = Feeder()
    feeder.DoWork()


if __name__ == "__main__":
    main()

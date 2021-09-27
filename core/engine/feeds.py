import logging
from datetime import datetime, timezone, timedelta
from core.database.database import create_db
from core.models.feed import FeedModel
from core.enums.feed_types import FeedTypes
from core.enums.statuses import BottifyStatus
from core.enums.config_key import ConfigKey
from core.database.crud.feeds import (
    update_feed_refresh_started,
    update_feed_refresh_complete,
    read_feed_by_id,
    update_feed_status,
    read_new_feeds,
    read_busy_feeds,
)
from core.database.crud.config_key import read_config_key
from core.feeds.helpers import get_mappings
from core.elasticsearch.utils import bulk_index
from core.elasticsearch.api import ElasticApiHelper


async def async_work_refresh_feed(feed_id: int):
    elastic = ElasticApiHelper()
    async with create_db() as database:
        feed = await read_feed_by_id(database, feed_id)
        if not feed:
            logging.error(
                f"Async Work Refresh Feed : Feed Does Not Exist : Feed ID {feed_id}"
            )
            return False
        updated = await update_feed_status(database, feed.id, BottifyStatus.Busy)
        if not feed.result_generator:
            logging.error(
                f"Async Work Refresh Feed : Tried to Refresh Feed with No Result Generator : Feed ID {feed.id}"
            )
            return False
        elastic.index_generator(
            feed.index_name,
            feed.result_generator(
                configs=feed.configs, database=database, index_name=feed.index_name
            ),
        )
        complete = await update_feed_refresh_complete(database, feed.id, True)
        logging.info(
            f"Async Work Refresh Feed : Refresh Completed Successfully : Feed ID {feed_id}"
        )
        return


async def async_work_set_feed_indexes():
    elastic = ElasticApiHelper()
    settings = {"index.mappings.single_type": "true"}
    async with create_db() as database:
        for feed in await read_new_feeds(database):
            mappings = get_mappings(feed)
            if not feed:
                logging.error(
                    f"Async Work Set Feed Indexes : Failed to Set Mappings for Feed : Feed ID {feed.id}"
                )
                continue
            if elastic.create_index(feed.index_name, mappings):
                await update_feed_status(database, feed.id, BottifyStatus.Active)
            else:
                await update_feed_status(database, feed.id, BottifyStatus.Error)


# NOTIMPLEMENTED holding off on this task until we encounter another problem with them sticking
async def async_work_release_stuck_feeds():
    async with create_db() as database:
        stuck_after_minutes_ck = await read_config_key(
            database, ConfigKey.FeedStuckAfterMinutes
        )
        if not stuck_after_minutes_ck:
            logging.error(
                f"Async Work Release Stuck Feeds : Failed to Load Required Config Key : Key Name {str(ConfigKey.FeedStuckAfterMinutes)}"
            )
            return
        stuck_feed_names = []
        feed_count = 0
        for feed in await read_busy_feeds(database):
            now = datetime.now(tz=timezone.utc)
            min_execution_time = now - timedelta(minutes=stuck_after_minutes_ck.value)
            if feed.last_executed_at < min_execution_time:
                stuck_feed_names.append(feed.name)
                await update_feed_status(database, feed.id, BottifyStatus.Active)
            feed_count += 1
        logging.info(
            f"Async Work Release Stuck Feeds : Completed Successfully : Total Feeds {feed_count} : Stuck Feeds {len(stuck_feed_names)} : Stuck Names {stuck_feed_names}"
        )
        return

import logging
from core.database.database import create_db
from core.models.feed import FeedModel
from core.enums.feed_types import FeedTypes
from core.enums.statuses import BottifyStatus
from core.database.crud.feeds import (
    update_feed_refresh_started,
    update_feed_refresh_complete,
    read_feed_by_id,
    update_feed_status,
    read_new_feeds,
)
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
        elastic.index_generator(feed.index_name, feed.result_generator(feed.configs))
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

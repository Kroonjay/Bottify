from core.database.tables.feeds import get_feeds_table
from core.database.helpers import build_model_from_row, write_db
from core.enums.statuses import BottifyStatus
from core.enums.feed_types import FeedTypes
from core.models.feed import FeedInModel, FeedModel
from databases import Database
from sqlalchemy import and_
import logging
import json
from typing import List
from datetime import datetime, timedelta, timezone

feed_table = get_feeds_table()


async def create_feed(database: Database, feed_in: FeedInModel):
    if not isinstance(feed_in, FeedInModel):
        logging.error(f"Create Feed : Input Must be FeedInModel - Got: {type(feed_in)}")
        return False
    query = feed_table.insert()
    return await write_db(database, query, feed_in.dict())


async def read_feed_by_id(database: Database, feed_id: int):
    query = feed_table.select().where(feed_table.c.id == feed_id).limit(1)
    row = await database.fetch_one(query)
    return build_model_from_row(row, FeedModel)


async def read_all_feeds(database: Database, limit: int):
    feeds = []
    query = feed_table.select().limit(limit)
    async for row in database.iterate(query):
        feeds.append(build_model_from_row(row, FeedModel))
    if not feeds:
        logging.error(f"Read All Feeds : No Results")
    return feeds


async def read_active_feeds(database: Database, limit: int = None) -> List[FeedModel]:
    feeds = []
    if limit:
        query = (
            feed_table.select()
            .where(feed_table.c.status == BottifyStatus.Active.value)
            .limit(limit)
        )
    else:
        query = feed_table.select().where(
            feed_table.c.status == BottifyStatus.Active.value
        )
    async for row in database.iterate(query):
        feeds.append(build_model_from_row(row, FeedModel))
    if not feeds:
        logging.error(f"Read Active Feeds : No Results")
    return feeds


async def read_new_feeds(database: Database) -> List[FeedModel]:
    query = feed_table.select().where(feed_table.c.status == BottifyStatus.New.value)
    feeds = []
    async for row in database.iterate(query):
        feeds.append(build_model_from_row(row, FeedModel))
    if not feeds:
        logging.error(f"Read New Feeds : No Results")
    return feeds


async def read_next_overdue_active_feed(database: Database):
    current_time = datetime.now(tz=timezone.utc)
    query = (
        feed_table.select()
        .where(
            and_(
                feed_table.c.next_execution_at <= current_time,
                feed_table.c.status == BottifyStatus.Active.value,
            )
        )
        .limit(1)
        .order_by(feed_table.c.next_execution_at.asc())
    )
    # print(query)
    row = await database.fetch_one(query)
    return build_model_from_row(row, FeedModel)


async def read_overdue_active_feeds(database: Database):
    feeds = []
    current_time = datetime.now(tz=timezone.utc)
    query = feed_table.select().where(
        and_(
            feed_table.c.next_execution_at <= current_time,
            feed_table.c.status == BottifyStatus.Active.value,
        )
    )

    async for row in database.iterate(query):
        feeds.append(build_model_from_row(row, FeedModel))
    if not feeds:
        logging.error(f"Read Overdue Active Feeds : No Results")
    return feeds


async def update_feed_status(
    database: Database, feed_id: int, new_status: BottifyStatus
):
    if not isinstance(new_status, BottifyStatus):
        print(
            f"Failed to Update Feed Status:New Status Must be a Member of BottifyStatus Enum:Got: {type(new_status)}"
        )
        return False
    query = (
        feed_table.update()
        .where(feed_table.c.id == feed_id)
        .values({"status": new_status.value})
    )
    updated_feed = await database.execute(query)
    print(f"Successfully Updated Feed:Updated Feed: {updated_feed}")
    return True


async def update_feed_refresh_started(database: Database, feed_id: int):
    feed_to_update = await read_feed_by_id(database, feed_id)
    if not feed_to_update:
        logging.error(
            f"Update Feed Refresh Started : Feed Does Not Exist : Feed ID: {str(feed_id)}"
        )
        return None

    if not feed_to_update.status == BottifyStatus.Active:
        logging.error(
            f"Update Feed Refresh Started : Tried to Refresh an Inactive Feed : Feed ID {str(feed_id)}"
        )
        return None
    query = (
        feed_table.update()
        .where(feed_table.c.id == feed_id)
        .values({"status": BottifyStatus.Busy.value})
    )
    await database.execute(query)
    logging.debug(f"Update Feed Refresh Started : Success : Feed ID: {feed_id}")
    return await read_feed_by_id(database, feed_id)


async def update_feed_refresh_complete(
    database: Database, feed_id: int, success: bool = True
):
    feed_to_update = await read_feed_by_id(database, feed_id)
    if not feed_to_update:
        logging.error(
            f"Update Feed Refresh Complete : No Feed to Update : Feed ID {feed_id}"
        )
        return False
    current_time = datetime.now(tz=timezone.utc)
    next_execution_time = current_time + timedelta(
        minutes=feed_to_update.update_interval
    )
    query = (feed_table.update().where(feed_table.c.id == feed_to_update.id)).values(
        {
            "status": BottifyStatus.Active.value
            if success
            else BottifyStatus.Error.value,
            "last_execution_at": current_time,
            "next_execution_at": next_execution_time,
        }
    )
    await database.execute(query)
    logging.info(
        f"Update Feed Refresh Complete : Success : Feed ID {feed_to_update.id} : New Status {BottifyStatus.Active if success else BottifyStatus.Error}"
    )
    return True


async def update_feed_configs(database: Database, feed_id: int, new_configs: dict):
    if not isinstance(new_configs, dict):
        logging.error(
            f"Update Feed Configs : New Config Input Must be a Dict : Got {type(new_configs)} : Feed ID {feed_id}"
        )
        return False
    feed = await read_feed_by_id(database, feed_id)
    if not feed:
        logging.error(f"Update Feed Configs : No Feed to Update : Feed ID {feed_id}")
        return False
    if not feed.configs:
        feed.configs = new_configs
    else:
        feed.configs.update(new_configs)
    if not feed.configs:
        logging.error(
            f"Update Feed Configs : Configs is None after Merging : Old Configs {feed.configs} : New Configs {new_configs}"
        )
        return False
    query = (
        feed_table.update()
        .where(feed_table.c.id == feed.id)
        .values({"configs": json.dumps(feed.configs)})
    )
    await database.execute(query)
    logging.info(f"Update Feed Configs : Complete : Feed ID {feed.id}")
    return True

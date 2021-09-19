from databases import Database
from sqlalchemy import and_
from uuid import UUID
import logging

from core.database.helpers import build_model_from_row, write_db
from core.database.tables.subscription import get_subscription_table
from core.models.subscription import (
    SubscriptionInModel,
    SubscriptionModel,
)

subscription_table = get_subscription_table()

logger = logging.getLogger("Bottify.Crud.Subscription")


async def create_subscription(database: Database, sub_in: SubscriptionInModel):
    if not isinstance(sub_in, SubscriptionInModel):
        logger.error(
            f"Create Alert Subscription : Input Must be SubscriptionInModel : Got {type(sub_in)}"
        )
        return False
    query = subscription_table.insert()
    return await write_db(database, query, sub_in.dict())


async def read_subscription_by_id(database: Database, sub_id: int):
    if not isinstance(sub_id, int):
        logger.error(
            f"Read Alert Subscription by ID : ID Must be an Integer : Got {type(sub_id)}"
        )
        return None
    query = (
        subscription_table.select().where(subscription_table.c.id == sub_id).limit(1)
    )
    row = await database.fetch_one(query)
    return build_model_from_row(row, SubscriptionModel)


async def read_all_subscriptions(database: Database, limit: int):
    subs = []
    if not isinstance(limit, int):
        logger.error(
            f"Read All Alert Subscriptions : Limit Must be an Integer : Got {type(limit)}"
        )
        return subs
    query = subscription_table.select().limit(limit)
    async for row in database.iterate(query):
        subs.append(build_model_from_row(row, SubscriptionModel))
    if not subs:
        logger.error(f"Read All Subscriptions : No Rows")
    return subs


async def read_subscriptions_by_monitor_id(database: Database, monitor_id: int):
    subs = []
    if not isinstance(monitor_id, int):
        logger.error(
            f"Read Alert Subscription by Monitor ID : Monitor ID Must be an Integer : Got {type(monitor_id)}"
        )
        return subs
    query = subscription_table.select().where(
        subscription_table.c.monitor_id == monitor_id
    )
    async for row in database.iterate(query):
        subs.append(build_model_from_row(row, SubscriptionModel))
    if not subs:
        logger.error(f"Read Alert Subscriptions By Monitor ID : No Results")
    return subs


async def read_subscriptions_by_strategy_id(database: Database, strategy_id: int):
    subs = []
    if not isinstance(monitor_id, int):
        logger.error(
            f"Read Alert Subscription by Strategy ID : Strategy ID Must be an Integer : Got {type(strategy_id)}"
        )
        return subs
    query = subscription_table.select().where(
        subscription_table.c.strategy_id == strategy_id
    )
    async for row in database.iterate(query):
        subs.append(build_model_from_row(row_data, SubscriptionModel))
    if not subs:
        logger.error(f"Read Alert Subscriptions By Strategy ID : No Results")
    return subs


async def read_subscription_by_monitor_strategy(
    database: Database, monitor_id: int, strategy_id: int
):
    if not isinstance(monitor_id, int):
        logger.error(
            f"Read Alert Subscription by Strategy ID : Strategy ID Must be an Integer : Got {type(strategy_id)}"
        )
        return subs
    query = (
        subscription_table.select()
        .where(
            and_(
                subscription_table.c.monitor_id == monitor_id,
                subscription_table.c.strategy_id == strategy_id,
            )
        )
        .limit(1)
    )
    row = await database.fetch_one(query)
    return build_model_from_row(row, SubscriptionModel)

from databases import Database
from sqlalchemy import and_
import logging

from core.database.helpers import build_model_from_row, write_db
from core.database.tables.monitor import get_monitor_table
from core.models.monitor import (
    MonitorInModel,
    MonitorModel,
)

monitor_table = get_monitor_table()


async def create_monitor(database: Database, sub_in: MonitorInModel):
    if not isinstance(sub_in, MonitorInModel):
        logging.error(
            f"Create Alert Subscription : Input Must be MonitorInModel : Got {type(sub_in)}"
        )
        return False
    query = monitor_table.insert()
    return await write_db(database, query, sub_in.dict())


async def read_monitor_by_id(database: Database, sub_id: int):
    if not isinstance(sub_id, int):
        logging.error(
            f"Read Alert Subscription by ID : ID Must be an Integer : Got {type(sub_id)}"
        )
        return None
    query = monitor_table.select().where(monitor_table.c.id == sub_id).limit(1)
    row = await database.fetch_one(query)
    return build_model_from_row(row, MonitorModel)


async def read_monitor_by_source_id(database: Database, source_id: str):
    if not isinstance(source_id, str):
        logging.error(
            f"Read Monitor by Source ID : Source ID Must be a String : Got {type(source_id)}"
        )
        return None
    query = monitor_table.select().where(monitor_table.c.source_id == source_id)
    row = await database.fetch_one(query)
    if not row:
        logging.error(f"Read Alert Subscriptions By Source ID : No Results")
    return build_model_from_row(row, MonitorModel)


async def read_all_monitors(database: Database, limit: int):
    monitors = []
    if not isinstance(limit, int):
        logging.error(
            f"Read All Monitors : Limit Must be an Integer : Got {type(limit)}"
        )
        return monitors
    query = monitor_table.select().limit(limit)
    async for row in database.iterate(query):
        monitors.append(build_model_from_row(row, MonitorModel))
    if not monitors:
        logging.error(f"Read All Monitors : No Results")
    return monitors


async def update_monitor(database: Database, monitor: MonitorModel):
    if not isinstance(monitor, MonitorModel):
        logging.error(
            f"Update Monitor : Monitor Input Must be a MonitorModel : Got {type(monitor)}"
        )
        return False
    query = (
        monitor_table.update()
        .where(monitor_table.c.id == monitor.id)
        .values(monitor.dict(exclude={"id", "source_id"}, exclude_defaults=True))
    )
    await database.execute(query)
    return True

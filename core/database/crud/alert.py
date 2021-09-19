from databases import Database
from sqlalchemy import and_
from typing import List
from datetime import timezone
import logging
from core.database.helpers import build_model_from_row, write_db
from core.database.tables.alert import get_alert_table
from core.models.alert import AlertInModel, AlertModel


alert_table = get_alert_table()


async def create_alert(database: Database, alert_in: AlertInModel):
    if not isinstance(alert_in, AlertInModel):
        logging.error(f"Create Alert:Input must be AlertInModel:Got: {type(alert_in)}")
        return False

    query = alert_table.insert()
    return await write_db(database, query, alert_in.dict())


async def read_alert_by_id(database: Database, alert_id: int):
    if not isinstance(alert_id, int):
        logging.error(
            f"Read Alert by ID : Alert ID Must be an Integer : Got: {type(alert_id)}"
        )
        return None
    query = alert_table.select().where(alert_table.c.id == alert_id).limit(1)
    row = await database.fetch_one(query)
    return build_model_from_row(row, AlertModel)


async def read_all_alerts(database: Database, limit: int):
    alerts = []
    if not isinstance(limit, int):
        logging.error(f"Read All Alerts:Limit Must be an Int - Got: {type(limit)}")
        return alerts
    query = alert_table.select().limit(limit)
    async for row in database.iterate(query):
        alerts.append(build_model_from_row(row, AlertModel))
    if not alerts:
        logging.error(f"Read All Alerts : No Results")
    return alerts


async def read_alerts_by_indicator_definition_id(
    database: Database, definition_id: int, limit: int
):
    alerts = []
    if not isinstance(definition_id, int):
        logging.error(
            f"Read Alerts by Indicator Definition : Definition ID Must be an Int - Got: {type(definition_id)}"
        )
        return alerts
    if not isinstance(limit, int):
        logging.error(
            f"Read Alerts by Indicator Definition : Limit Must be an Int - Got: {type(limit)}"
        )
        return alerts
    query = (
        alert_table.select()
        .where(alert_table.c.definition_id == definition_id)
        .limit(limit)
    )
    async for row in database.iterate(query):
        alerts.append(build_model_from_row(row, AlertModel))
    if not alerts:
        logging.error(f"Read Alerts by Indicator Definition : No Results")
    return alerts


async def read_alerts_by_monitor_id(database: Database, monitor_id: str, limit: int):
    alerts = []

    if not isinstance(monitor_id, str):
        logging.error(
            f"Read Alerts by Monitor ID : Monitor ID Must be a String - Got: {type(monitor_id)}"
        )
        return alerts
    if not isinstance(limit, int):
        logging.error(
            f"Read Alerts by Monitor ID : Limit Must be an Int - Got: {type(limit)}"
        )
        return alerts

    query = (
        alert_table.select().where(alert_table.c.monitor_id == monitor_id).limit(limit)
    )
    async for row in database.iterate(query):
        alerts.append(build_model_from_row(row, AlertModel))
    if not alerts:
        logging.error(f"Read Alerts by Monitor ID: No Results")
    return alerts

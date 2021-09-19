from databases import Database
from sqlalchemy import and_
from typing import List
import logging

from core.database.helpers import build_model_from_row, write_db
from core.database.tables.indicator import get_indicator_table
from core.models.indicator import IndicatorInModel, IndicatorModel
from core.enums.statuses import BottifyStatus

indicator_table = get_indicator_table()


async def create_indicator(database: Database, indicator_in: IndicatorInModel):
    if not isinstance(indicator_in, IndicatorInModel):
        logging.error(
            f"Create Indicator:Input must be IndicatorInModel:Got: {type(indicator_in)}"
        )
        return False

    query = indicator_table.insert()
    return await write_db(database, query, indicator_in.dict())


async def read_indicator_by_id(database: Database, indicator_id: int):
    if not isinstance(indicator_id, int):
        logging.error(
            f"Read Indicator by ID : ID must be an Int : Got {type(indicator_id)}"
        )
        return None
    query = (
        indicator_table.select().where(indicator_table.c.id == indicator_id).limit(1)
    )
    row = await database.fetch_one(query)
    return build_model_from_row(row, IndicatorModel)


async def read_all_indicators(database: Database, limit: int):
    indicators = []
    if not isinstance(limit, int):
        logging.error(f"Read All Indicators:Input Must be an Int - Got: {type(limit)}")
        return indicators
    query = indicator_table.select().limit(limit)
    async for row in database.iterate(query):
        indicators.append(build_model_from_row(row, IndicatorModel))
    if not indicators:
        logging.error(f"Read All Indicators:No Results")
    return indicators


async def read_indicators_by_strategy_id(
    database: Database, strategy_id: int, limit: int
):
    indicators = []
    if not isinstance(strategy_id, int):
        logging.error(
            f"Read All Indicators:Input Must be an Int - Got: {type(strategy_id)}"
        )
        return indicators
    if not isinstance(limit, int):
        logging.error(
            f"Read Indicators By Strategy ID : Limit Must be an Int : Got {type(limit)}"
        )
        return indicators
    query = (
        indicators.select()
        .where(indicator_table.c.strategy_id == strategy_id)
        .limit(limit)
    )
    async for row in database.iterate(query):
        indicators.append(build_model_from_row(row, IndicatorModel))
    if not indicators:
        logging.error(f"Read Indicators By Strategy ID : No Results")
    return indicators


async def read_indicators_by_strategy_ids(
    database: Database, strategy_ids: List[int], limit: int
):
    indicators = []

    query = (
        indicator_table.select()
        .where(indicator_table.c.strategy_id.in_([strategy_ids]))
        .limit(limit)
    )
    async for row in database.iterate(query):
        indicators.append(build_model_from_row(row, IndicatorModel))
    if not indicators:
        logging.error(f"Read Indicators By Strategy IDs : No Results")
    return indicators


async def read_active_indicators_by_definition_id(
    database: Database, definition_id: str
):
    indicators = []

    query = indicator_table.select().where(
        and_(
            indicator_table.c.definition_id == definition_id,
            indicator_table.c.status == BottifyStatus.Active.value,
        )
    )
    async for row in database.iterate(query):
        indicators.append(build_model_from_row(row, IndicatorModel))
    if not indicators:
        logging.error(
            f"Read Active Indicators By Definition ID : No Results : Definition ID {str(definition_id)}"
        )
    return indicators


async def update_indicator_status_by_strategy_id(
    database: Database, strategy_id: int, new_status: BottifyStatus
):
    if not isinstance(new_status, BottifyStatus):
        logging.error(
            f"Update Indicator Status By Strategy ID : New Status Must be Type BottifyStatus - Got: {type(new_status)}"
        )
    query = (
        indicator_table.update()
        .where(indicator_table.c.strategy_id == strategy_id)
        .values(status=new_status.value)
    )
    success = await write_db(database, query)
    if not success:
        logging.error(f"Update Indicator Status By Strategy ID : Write DB Failure")
    return success


async def update_indicator_status_by_definition_id(
    database: Database, definition_id: int, new_status: BottifyStatus
):
    if not isinstance(new_status, BottifyStatus):
        logging.error(
            f"Update Indicator Status By Definition ID : New Status Must be Type BottifyStatus - Got: {type(new_status)}"
        )
    query = (
        indicator_table.update()
        .where(indicator_table.c.definition_id == definition_id)
        .values(status=new_status.value)
    )
    success = await write_db(database, query)
    if not success:
        logging.error(f"Update Indicator Status By Definition ID : Write DB Failure")
    return success

import logging
from databases import Database
from typing import List
from core.database.helpers import build_model_from_row, write_db
from core.database.tables.indicator_definition import get_indicator_definition_table
from core.models.indicator import IndicatorDefinitionInModel, IndicatorDefinitionModel
from core.database.crud.indicator import update_indicator_status_by_definition_id
from core.enums.statuses import BottifyStatus

indicator_def_table = get_indicator_definition_table()


async def create_indicator_definition(
    database: Database, indicator_def_in: IndicatorDefinitionInModel
):
    if not isinstance(indicator_def_in, IndicatorDefinitionInModel):
        logging.error(
            f"Create Indicator Definition : Input Must be Type IndicatorDefinitionInModel : Got {type(indicator_in)}"
        )
        return False
    query = indicator_def_table.insert()
    return await write_db(database, query, indicator_def_in.dict())


async def read_indicator_definition_by_id(database: Database, definition_id: int):
    if not isinstance(definition_id, int):
        logging.error(
            f"Read Indicator Definition by ID : ID must be an Int : Got {type(definition_id)}"
        )
        return None
    query = (
        indicator_def_table.select()
        .where(indicator_def_table.c.id == definition_id)
        .limit(1)
    )
    row = await database.fetch_one(query)
    return build_model_from_row(row, IndicatorDefinitionModel)


async def read_indicator_definition_by_monitor_id(database: Database, monitor_id: str):
    if not isinstance(monitor_id, str):
        logging.error(
            f"Read Indicator Definition by Monitor ID : Monitor ID Must be a String : Got {type(monitor_id)}"
        )
        return None
    query = (
        indicator_def_table.select()
        .where(indicator_def_table.c.monitor_id == monitor_id)
        .limit(1)
    )
    row = await database.fetch_one(query)
    return build_model_from_row(row, IndicatorDefinitionModel)


async def read_indicator_definitions_by_ids(
    database: Database, definition_ids: List[int], limit: int
):
    indicator_defs = []
    if not isinstance(definition_ids, list):
        logging.error(
            f"Read Indicator Definitions By IDs : IDs Must be a List of Integers : Got {type(definition_ids)}"
        )
        return indicator_defs
    query = (
        indicator_def_table.select()
        .where(indicator_def_table.c.id.in_(definition_ids))
        .limit(limit)
    )
    async for row in database.iterate(query):
        indicator_defs.append(build_model_from_row(row, IndicatorDefinitionModel))
    if not indicator_defs:
        logging.error(f"Read Indicator Definitions by Ids : No Results")
    return indicator_defs


async def read_all_indicator_definitions(database: Database, limit: int):
    indicator_defs = []
    if not isinstance(limit, int):
        logging.error(
            f"Read All Indicator Definitions : Limit Must be an Int : Got {type(limit)}"
        )
        return indicator_defs
    query = indicator_def_table.select().limit(limit)
    async for row in database.iterate(query):
        indicator_defs.append(build_model_from_row(row, IndicatorDefinitionModel))
    if not indicator_defs:
        logging.error(f"Read All Indicator Definitions : No Results")
    return indicator_defs


async def read_indicator_definitions_by_strategy_id(
    database: Database, strategy_id: int, limit: int
):
    indicator_defs = []
    if not isinstance(strategy_id, int):
        logging.error(
            f"Read Indicator Definitions by Strategy ID : Strategy ID Must be an Int : Got {type(strategy_id)}"
        )
        return indicator_defs
    if not isinstance(limit, int):
        logging.error(
            f"Read Indicator Definitions by Strategy ID : Limit Must be an Int : Got {type(limit)}"
        )
        return indicator_defs
    query = (
        indicator_def_table.select()
        .where(indicator_def_table.c.strategy_id == strategy_id)
        .limit(limit)
    )
    async for row in database.iterate(query):
        indicator_defs = build_model_from_row(row, IndicatorDefinitionModel)
    if not indicator_defs:
        logging.error(f"Read All Indicator Definitions : No Results")
    return indicator_defs


# Used to Update Status of an Indicator Definition, also Updates Status of all Indicators using that Definition
async def update_indicator_definition_status_by_id(
    database: Database, definition_id: int, new_status: BottifyStatus
):
    if not isinstance(definition_id, int):
        logging.error(
            f"Update Indicator Definition Status by ID : ID Must be an Int : Got {type(definition_id)}"
        )
        return False
    if not isinstance(new_status, BottifyStatus):
        logging.error(
            f"Update Indicator Definition Status by Id : New Status Must be Type BottifyStatus : Got {type(new_status)}"
        )
        return False
    query = (
        indicator_def_table.update()
        .where(indicator_def_table_id.c.id == definition_id)
        .values(status=new_status)
    )
    success = await write_db(database, query)
    if not success:
        logging.error(f"Update Indicator Definition Status by ID : Write DB Failure")
        return False
    success = await update_indicator_status_by_definition_id(
        database, definition_id, new_status
    )
    if not success:
        logging.error(
            f"Update Indicator Definition Status by ID : Update Indicator Failure"
        )
        return False
    return True

from core.models.strategy import StrategyInModel, StrategyModel, StrategyCreateModel
from core.database.tables.strategy import get_strategy_table
from core.database.helpers import build_model_from_row, write_db
from databases import Database
from uuid import UUID
import logging
from datetime import datetime, timedelta

strategy_table = get_strategy_table()


async def create_strategy(database: Database, strategy_in: StrategyInModel):
    if not isinstance(strategy_in, StrategyInModel):
        logging.error(
            f"Create Strategy:Strategy Input must be StrategyInModel:Got: {type(strategy_in)}"
        )
        return

    query = strategy_table.insert()
    success = await write_db(database=database, query=query, values=strategy_in.dict())
    if success:
        logging.info("Successfully Created Strategy")
        return True
    return False


async def read_strategy_by_id(database: Database, strategy_id: int):
    if not isinstance(strategy_id, int):
        logging.error(
            f"Read Strategy By ID:Strategy ID Must be an Integer:Got: {type(strategy_id)}"
        )
        return None
    query = strategy_table.select().where(strategy_table.c.id == strategy_id).limit(1)
    result_row = await database.fetch_one(query=query)
    if not result_row:
        logging.info(
            f"Read Strategy By ID:No Strategy Rows Found for ID:ID: {str(strategy_id)}"
        )
        return None
    strategy = build_model_from_row(result_row, StrategyModel)
    if not strategy:
        logging.error(
            f"Read Strategy by ID:Failed to Build Strategy Model from Row:Row Data: {result_row}"
        )
        return None
    return strategy


async def read_strategy_by_guid(database: Database, strategy_guid: UUID):
    if not isinstance(strategy_guid, UUID):
        logging.error(
            f"Read Strategy By GUID:Strategy GUID Must be Type UUID:Got: {type(strategy_guid)}"
        )
        return None
    query = (
        strategy_table.select().where(strategy_table.c.guid == strategy_guid).limit(1)
    )
    result_row = await database.fetch_one(query=query)
    if not result_row:
        logging.info(
            f"Read Strategy By GUID:No Strategy Rows Found for GUID:ID: {str(strategy_guid)}"
        )
        return None
    strategy = build_model_from_row(result_row, StrategyModel)
    if not strategy:
        logging.error(
            f"Read Strategy by GUID:Failed to Build Strategy Model from Row:Row Data: {result_row}"
        )
        return None
    return strategy


async def read_all_strategies(database: Database, limit: int):
    query = strategy_table.select().limit(limit)
    strategies = []
    async for row in database.iterate(query):
        strategies.append(build_model_from_row(row, StrategyModel))
    if not strategies:
        logging.error(f"Read Strategies:No Strategies Found in Database")
    return strategies


async def read_user_strategies(database: Database, user_id: int):
    if not isinstance(user_id, int):
        logging.error(
            f"Read User Strategies:User ID Must be an Integer:Got: {type(user_guid)}"
        )
        return None
    query = strategy_table.select().where(strategy_table.c.user_id == user_id)
    async for row in database.iterate(query):
        strategies.append(build_model_from_row(row, StrategyModel))
    if not strategies:
        logging.error(f"Read User Strategies:No Strategies Found in Database")
    return strategies

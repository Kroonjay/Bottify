import logging

from databases import Database
from uuid import UUID
from core.database.helpers import build_model_from_row, write_db
from core.database.tables.trade import get_trade_table
from core.models.trade import TradeInModel, TradeModel

trade_table = get_trade_table()


async def create_trade(database: Database, trade_in: TradeInModel):
    if not isinstance(trade_in, TradeInModel):
        logging.error(
            f"Create Trade : Input Must be a TradeInModel : Got {type(trade_in)}"
        )
        return False
    query = trade_table.insert()
    return await write_db(database, query, trade_in.dict())


async def read_all_trades(database: Database, limit: int):
    trades = []
    if not isinstance(limit, int):
        logging.error(f"Read All Trades : Limit Must be an Int : Got {type(limit)}")
        return trades
    query = trade_table.select().limit(limit)
    async for row in database.iterate(query):
        trades.append(build_model_from_row(row, TradeModel))
    if not trades:
        logging.error(f"Read All Trades : No Results")
    return trades


async def read_trade_by_id(database: Database, trade_id: int):
    if not isinstance(trade_id, int):
        logging.error(
            f"Read Trade by ID : Trade ID Must be an Integer : Got {type(trade_id)}"
        )
        return None
    query = trade_table.select().where(trade_table.c.id == trade_id).limit(1)
    row = await database.fetch_one(query)
    return build_model_from_row(row, TradeModel)


async def read_trade_by_source_id(database: Database, trade_source_id: str):
    if not isinstance(trade_source_id, str):
        logging.error(
            f"Read Trade by Source ID : Trade Source ID Must be a String : Got {type(trade_source_id)}"
        )
        return None
    query = (
        trade_table.select().where(trade_table.c.source_id == trade_source_id).limit(1)
    )
    row = await database.fetch_one(query)
    return build_model_from_row(row, TradeModel)

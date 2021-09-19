import logging

from databases import Database
from sqlalchemy import and_
from core.database.helpers import build_model_from_row, write_db
from core.database.tables.market import get_market_table
from core.models.market import MarketInModel, MarketModel

market_table = get_market_table()


async def create_market(database: Database, market_in: MarketInModel):
    if not isinstance(market_in, MarketInModel):
        logging.error(
            f"Create Market : Input Must be a MarketInModel : Got {type(market_in)}"
        )
        return False
    query = market_table.insert()
    return await write_db(database, query, market_in.dict())


async def read_all_markets(database: Database, limit: int):
    markets = []
    if not isinstance(limit, int):
        logging.error(
            f"Read All Markets : Limit Must be an Integer : Got {type(limit)}"
        )
        return markets
    query = market_table.select().limit(limit)
    async for row in database.iterate(query):
        markets.append(build_model_from_row(row, MarketModel))
    if not markets:
        logging.error(f"Read All Markets : No Results")
    return markets


async def read_markets_by_exchange(
    database: Database, exchange_id: int, limit: int = None
):
    markets = []
    if not isinstance(exchange_id, int):
        logging.error(
            f"Read Markets by Exchange : Exchange ID Must be an Integer : Got {type(exchange_id)}"
        )
        return markets

    query = market_table.select().where(market_table.c.exchange_id == exchange_id)
    async for row in database.iterate(query):
        markets.append(build_model_from_row(row, MarketModel))
    if not markets:
        logging.error(f"Read Markets by Exchange : No Results")
    return markets


async def read_market_by_id(database: Database, market_id: int):
    if not isinstance(market_id, int):
        logging.error(
            f"Read Market by ID : Market ID Must be an Integer : Got {type(market_id)}"
        )
        return None
    query = market_table.select().where(market_table.c.id == market_id).limit(1)
    row = await database.fetch_one(query)
    return build_model_from_row(row, MarketModel)


async def read_market_by_exchange_symbol(
    database: Database, exchange_id: int, symbol: str
):
    if not isinstance(exchange_id, int):
        logging.error(
            f"Read Market by Exchange Symbol : Exchange ID Must be an Integer : Got {type(symbol)}"
        )
        return None
    if not isinstance(symbol, str):
        logging.error(
            f"Read Market by Exchange Symbol : Symbol Must be a String : Got {type(symbol)}"
        )
        return None
    query = (
        market_table.select()
        .where(
            and_(
                market_table.c.exchange_id == exchange_id,
                market_table.c.symbol == symbol,
            )
        )
        .limit(1)
    )
    row = await database.fetch_one(query)
    return build_model_from_row(row, MarketModel)


async def update_market(database: Database, market_id: int, market_in: MarketInModel):
    if not isinstance(market_in, MarketInModel):
        logging.error(
            f"Update Market : Input Must be a MarketInModel : Got {type(market_in)}"
        )
        return False
    query = (
        market_table.update()
        .where(market_table.c.id == market_id)
        .values(
            market_in.dict(exclude={"symbol", "created_at", "tags"}, exclude_unset=True)
        )
    )
    success = await database.execute(query)
    return True


async def read_market_by_base_quote_exchange_ids(
    database: Database, base_currency_id: int, quote_currency_id: int, exchange_id: int
):
    if not isinstance(base_currency_id, int):
        logging.error(
            f"Read Market by Base Quote IDs : Base Currency ID Must be an Integer : Got {type(base_currency_id)}"
        )
        return None
    if not isinstance(quote_currency_id, int):
        logging.error(
            f"Read Market by Base Quote IDs : Quote Currency ID Must be an Integer : Got {type(quote_currency_id)}"
        )
        return None
    if not isinstance(exchange_id, int):
        logging.error(
            f"Read Market by Base Quote IDs : Exchange ID Must be an Integer : Got {type(exchange_id)}"
        )
        return None
    query = (
        market_table.select()
        .where(
            and_(
                market_table.c.base_currency_id == base_currency_id,
                market_table.c.quote_currency_id == quote_currency_id,
                market_table.c.exchange_id == exchange_id,
            )
        )
        .limit(1)
    )
    row = await database.fetch_one(query)
    return build_model_from_row(row, MarketModel)

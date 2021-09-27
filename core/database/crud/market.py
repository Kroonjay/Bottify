import logging

from databases import Database
from sqlalchemy import and_
from core.database.helpers import build_model_from_row, write_db
from core.database.tables.market import get_market_table
from core.models.market import MarketInModel, MarketModel
from core.enums.statuses import BottifyStatus

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


async def read_markets_by_status(database: Database, status: BottifyStatus):
    markets = []
    if not isinstance(status, BottifyStatus):
        logging.error(
            f"Read Markets by Status : Status Must be type BottifyStatus : Got {type(status)}"
        )
        return markets
    query = market_table.select().where(market_table.c.status == status.value)
    async for row in database.iterate(query):
        markets.append(build_model_from_row(row, MarketModel))
    if not markets:
        logging.debug("Read Markets by Status : No Results")
    return markets


async def read_active_markets(database: Database):
    return await read_markets_by_status(database, BottifyStatus.Active)


async def read_markets_by_tags(database: Database, input_tags: list):
    markets = []
    if not isinstance(input_tags, list):
        logging.error(
            f"Read Markets with Tags : Tags must be a List of Strings : Got {type(input_tags)}"
        )
        return markets
    query = market_table.select().where(market_table.c.tags != None)
    async for row in database.iterate(query):
        market = build_model_from_row(row, MarketModel)
        if not market:
            continue
        for tag in market.tags:
            if tag in input_tags:
                markets.append(build_model_from_row(row, MarketModel))
    if not markets:
        logging.debug("Read Markets with Tags : No Results")
    return markets


def sync_read_markets_by_tags(connection, input_tags: list):
    markets = []
    if not isinstance(input_tags, list):
        logging.error(
            f"Read Markets with Tags : Tags must be a List of Strings : Got {type(input_tags)}"
        )
        return markets
    query = market_table.select().where(market_table.c.tags != None)
    for row in connection.execute(query):
        market = build_model_from_row(row, MarketModel)
        if not market:
            continue
        for tag in market.tags:
            if tag in input_tags:
                markets.append(build_model_from_row(row, MarketModel))
    if not markets:
        logging.debug("Read Markets with Tags : No Results")
    return markets


async def read_markets_by_exchange_tags(
    database: Database, exchange_id: int, input_tags: list
):
    markets = []
    if not isinstance(input_tags, list):
        logging.error(
            f"Read Markets by Exchange Tags : Input Tags Must be a List of Strings : Got {type(input_tags)}"
        )
        return markets
    query = market_table.select().where(
        market_table.c.exchange_id == exchange_id, market_table.c.tags != None
    )
    async for row in database.iterate(query):
        market = build_model_from_row(row, MarketModel)
        if not market:
            continue
        for tag in market.tags:
            if tag in input_tags:
                markets.append(build_model_from_row(row, MarketModel))
    if not markets:
        logging.debug("Read Markets by Exchange Tags : No Results")
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

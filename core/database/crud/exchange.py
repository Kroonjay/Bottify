import logging

from databases import Database
from sqlalchemy import and_
from core.database.helpers import build_model_from_row, write_db
from core.database.tables.exchange import get_exchange_table
from core.models.exchange import ExchangeInModel, ExchangeModel
from core.enums.statuses import BottifyStatus
from core.enums.exchanges import Exchange

exchange_table = get_exchange_table()


async def create_exchange(database: Database, exchange_in: ExchangeInModel):
    if not isinstance(exchange_in, ExchangeInModel):
        logging.error(
            f"Create Exchange : Input Must be ExchangeInModel : Got {type(exchange_in)}"
        )
        return False
    query = exchange_table.insert()
    return await write_db(database, query, exchange_in.dict())


async def read_all_exchanges(database: Database, limit: int):
    exchanges = []
    if not isinstance(limit, int):
        logging.error(f"Read All Exchanges : Limit Must be an Int : Got {type(limit)}")
        return exchanges
    query = exchange_table.select().limit(limit)
    async for row in database.iterate(query):
        exchanges.append(build_model_from_row(row, ExchangeModel))
    if not exchanges:
        logging.error(f"Read All Exchanges : No Results")
    return exchanges


async def read_all_active_exchanges(database: Database):
    exchanges = []
    query = exchange_table.select().where(
        exchange_table.c.status == BottifyStatus.Active.value
    )
    async for row in database.iterate(query):
        exchanges.append(build_model_from_row(row, ExchangeModel))
    if not exchanges:
        logging.error(f"Read All Active Exchanges : No Results")
    return exchanges


async def read_active_exchange_by_user_exchange_type(
    database: Database, user_id: int, exchange_type: Exchange
):
    if not isinstance(exchange_type, Exchange):
        logging.error(
            f"Read Active Exchange by User Exchange Type : Exchange Type Input must be Exchange Enum Member : Got {type(exchange_type)}"
        )
        return None
    query = (
        exchange_table.select()
        .where(
            and_(
                exchange_table.c.status == BottifyStatus.Active.value,
                exchange_table.c.exchange_type == exchange_type,
                exchange_table.c.user_id == user_id,
            )
        )
        .limit(1)
    )
    row = await database.fetch_one(query)
    return build_model_from_row(row, ExchangeModel)


async def read_exchange_by_id(database: Database, exchange_id: int):
    if not isinstance(exchange_id, int):
        logging.error(
            f"Read Exchange by ID : Exchange ID Must be an Integer : Got {type(exchange_id)}"
        )
        return None
    query = exchange_table.select().where(exchange_table.c.id == exchange_id).limit(1)
    row = await database.fetch_one(query)
    return build_model_from_row(row, ExchangeModel)


def sync_read_exchange_by_id(connection, exchange_id: int):
    query = exchange_table.select().where(exchange_table.c.id == exchange_id).limit(1)
    results = connection.execute(query)
    for row in results:
        return build_model_from_row(row, ExchangeModel)


async def read_active_exchanges_by_user(database: Database, user_id: int):
    exchanges = []
    if not isinstance(user_id, int):
        logging.error(
            f"Read Exchanges by User : User ID Must be an Integer : Got {type(user_id)}"
        )
        return exchanges
    query = exchange_table.select().where(
        and_(
            exchange_table.c.user_id == user_id,
            exchange_table.c.status == BottifyStatus.Active.value,
        )
    )
    async for row in database.iterate(query):
        exchanges.append(build_model_from_row(row, ExchangeModel))
    if not exchanges:
        logging.error(f"Read Exchanges by User : No Results : User ID {str(user_id)}")
    return exchanges

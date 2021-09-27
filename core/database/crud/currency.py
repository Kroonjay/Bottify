import logging

from databases import Database

from core.database.helpers import build_model_from_row, write_db
from core.models.currency import CurrencyInModel, CurrencyModel

from core.database.tables.currency import get_currency_table

currency_table = get_currency_table()


async def create_currency(database: Database, currency_in: CurrencyInModel):
    if not isinstance(currency_in, CurrencyInModel):
        logging.error(
            f"Create Currency : Input Must be Type CurrencyInModel : Got {type(currency_in)}"
        )
        return False
    query = currency_table.insert()
    return await write_db(database, query, currency_in.dict())


async def read_currency_by_id(database: Database, currency_id: int):
    if not isinstance(currency_id, int):
        logging.error(
            f"Read Currency by ID : Currency ID Must be an Integer : Got {type(currency_id)}"
        )
        return None
    query = currency_table.select().where(currency_table.c.id == currency_id).limit(1)
    row = await database.fetch_one(query)
    return build_model_from_row(row, CurrencyModel)


async def read_currency_by_symbol(database: Database, symbol: str):
    if not isinstance(symbol, str):
        logging.error(
            f"Read Currency by Symbol : Symbol Must be a String : Got {type(symbol)}"
        )
        return None
    query = currency_table.select().where(currency_table.c.symbol == symbol).limit(1)
    row = await database.fetch_one(query)
    return build_model_from_row(row, CurrencyModel)


async def read_all_currencies(database: Database, limit: int):
    currencies = []
    if not isinstance(limit, int):
        logging.error(
            f"Read All Currencies : Limit Must be an Integer : Got {type(limit)}"
        )
        return currencies
    query = currency_table.select().limit(limit)
    async for row in database.iterate(query):
        currencies.append(build_model_from_row(row, CurrencyModel))
    if not currencies:
        logging.error(f"Read All Currencies : No Results")
    return currencies


async def read_currencies_by_tags(database: Database, input_tags: list, limit: int):
    currencies = []
    if not isinstance(input_tags, list):
        logging.error(
            f"Read Currencies with Tags : Tags must be a List of Strings : Got {type(input_tags)}"
        )
        return currencies
    for currency in await read_all_currencies(database, limit):
        if not currency.tags:
            continue
        for tag in currency.tags:
            if tag in input_tags:
                currencies.append(currency)
    if not currencies:
        logging.debug("Read Currencies with Tags : No Results")
    return currencies

import logging
from pydantic import ValidationError
from databases import Database

from core.database.database import create_db
from core.database.crud.exchange import read_exchange_by_id, read_all_active_exchanges
from core.database.crud.currency import read_currency_by_symbol
from core.database.crud.market import (
    read_market_by_exchange_symbol,
    create_market,
    update_market,
)
from core.exchanges.helpers import transform_exchange_market


async def async_work_update_exchange_markets(exchange_id: int, database: Database):

    exchange = await read_exchange_by_id(database, exchange_id)
    if not exchange:
        logging.error(
            f"Update Exchange Markets : No Exchange Row for ID : ID {str(exchange_id)}"
        )
        return False
    exchange_markets = exchange.api(exchange).get_markets()
    for exchange_market in exchange_markets:
        base_currency = await read_currency_by_symbol(
            database, exchange_market.base_currency_symbol
        )
        if not base_currency:
            logging.debug(
                f"Update Exchange Markets : No Currency Row for Base Currency : Symbol {exchange_market.base_currency_symbol}"
            )
            continue
        quote_currency = await read_currency_by_symbol(
            database, exchange_market.quote_currency_symbol
        )
        if not quote_currency:
            logging.debug(
                f"Update Exchange Markets : No Currency Row for Quote Currency : Symbol {exchange_market.quote_currency_symbol}"
            )
            continue
        new_market = transform_exchange_market(
            exchange_market,
            exchange.id,
            exchange.exchange_type,
            base_currency.id,
            quote_currency.id,
        )
        if not new_market:
            logging.error(f"Update Exchange Markets : Market Transform Failed")
            continue
        db_market = await read_market_by_exchange_symbol(
            database, exchange.id, new_market.symbol
        )
        if not db_market:
            logging.info(
                f"Update Exchange Markets : No Market Row for Exchange Market, Creating : Symbol {new_market.symbol} : Exchange ID {exchange.id}"
            )
            success = await create_market(database, new_market)
            if not success:
                logging.error(f"Update Exchange Markets : Failed to Create New Market")
        else:
            await update_market(database, db_market.id, new_market)


async def async_work_update_all_markets():
    async with create_db() as database:
        exchanges = await read_all_active_exchanges(database)
        for exchange in exchanges:
            await async_work_update_exchange_markets(exchange.id, database)

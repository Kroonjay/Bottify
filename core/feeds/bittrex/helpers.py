import asyncio
import logging
from core.database.database import create_db
from core.database.crud.exchange import read_exchange_by_id
from core.database.crud.market import read_markets_by_exchange


async def async_fetch_markets(exchange_id: int):
    async with create_db() as database:
        exchange = await read_exchange_by_id(database, exchange_id)
        if not exchange:
            logging.error(
                f"Bittrex Fetch Markets : Failed to Load Exchange : Exchange ID {exchange_id}"
            )
            return None
        markets = await read_markets_by_exchange(database, exchange_id)
        if not markets:
            logging.error(
                f"Bittrex Fetch Markets : Failed to Load Markets : Exchange ID {exchange_id}"
            )
            return None
        return {"exchange": exchange, "markets": markets}


def fetch_markets(exchange_id: int):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(async_fetch_markets(exchange_id))

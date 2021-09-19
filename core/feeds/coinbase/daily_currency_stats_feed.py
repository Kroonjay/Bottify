import asyncio
import logging
import nest_asyncio

nest_asyncio.apply()
from core.database.database import create_db
from core.feeds.helpers import action_wrapper
from core.database.crud.exchange import read_exchange_by_id
from core.database.crud.market import read_markets_by_exchange
from core.exchanges.coinbase.api import CoinbaseApiHelper
from core.feeds.coinbase.public_trades_feed import fetch_products


def daily_currency_stats_result_generator(configs: dict):
    exchange_id = configs.get("exchange_id")
    if not exchange_id:
        logging.error(
            "Daily Currency Stats Result Generator : Required Exchange ID is Missing from Feed Configs"
        )
        return
    loop = asyncio.get_event_loop()
    feed_data = loop.run_until_complete(fetch_products(exchange_id))
    if not feed_data:
        logging.error(
            "Daily Currency Stats Result Generator : Failed to Fetch Feed Data from Database"
        )
        return
    exchange = feed_data.get("exchange")
    if not exchange:
        logging.error(
            "Daily Currency Stats Result Generator : Exchange is Missing or None"
        )
        return
    markets = feed_data.get("markets")
    if not markets:
        logging.error(
            f"Daily Currency Stats Result Generator : Markets are Missing or None"
        )
        return
    for market in markets:
        stats = exchange.api(exchange).get_daily_currency_stats(market.symbol)
        yield action_wrapper(stats)

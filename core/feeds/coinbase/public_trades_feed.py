import asyncio
import logging

from core.database.database import create_db
from core.database.crud.exchange import read_exchange_by_id
from core.database.crud.market import read_markets_by_exchange
from core.exchanges.coinbase.api import CoinbaseApiHelper
from core.feeds.helpers import action_wrapper
from core.elasticsearch.api import ElasticApiHelper


async def fetch_products(exchange_id: int):
    async with create_db() as database:
        exchange = await read_exchange_by_id(database, exchange_id)
        if not exchange:
            logging.error(
                f"Coinbase Public Trade Result Generator : Fetch Markets : Failed to Load Exchange : Exchange ID {exchange_id}"
            )
            return None
        markets = await read_markets_by_exchange(database, exchange_id)
        return {"exchange": exchange, "markets": markets}


def fetch_last_trade_id(es_client, index_name, market_symbol):
    template_name = "coinbase-last-trade-id"
    market_symbol_param_name = "market_symbol"
    params = {market_symbol_param_name: market_symbol}
    results = es_client.template_search(template_name, index_name, params)
    if not results:
        return None
    else:
        if not results[0].get("_source"):
            logging.error("Fetch Last Trade ID : Response Has No Source Fields")
            return None
        return results[0].get("_source").get("trade_id")


def coinbase_public_trade_result_generator(configs: dict):
    exchange_id = configs.get("exchange_id")
    if not exchange_id:
        logging.error(
            "Coinbase Public Trade Result Generator : Required Exchange ID Missing from Feed Configs"
        )
        return
    loop = asyncio.get_event_loop()
    feed_data = loop.run_until_complete(fetch_products(exchange_id))
    if not feed_data:
        logging.error(
            "Coinbase Public Trade Result Generator : Failed to Fetch Feed Data from Database"
        )
        return
    exchange = feed_data.get("exchange")
    if not exchange:
        logging.error(
            "Coinbase Public Trade Result Generator : Exchange is Missing or None"
        )
        return
    markets = feed_data.get("markets")
    if not markets:
        logging.error(
            "Coinbase Public Trade Result Generator : Markets are Missing or None"
        )
        return
    limit = configs.get("limit")
    index_name = configs.get("index_name")
    if not index_name:
        logging.error(
            f"Coinbase Public Trade Result Generator : Required config key 'index_name' is missing or None"
        )
        return
    es_client = ElasticApiHelper()
    task_limit = configs.get(
        "task_limit"
    )  # Different from Coinbase API limit, keeps Elastic from getting overwhelmed as this request can return over 100k results
    if not task_limit:
        logging.error(
            f"Public Trade Result Generator : Required config key 'task_limit' is missing or None"
        )
        return
    task_counter = 0
    market_counter = 0
    min_trade_id = 0
    max_trade_id = 0
    market_counters = {}
    for market in markets:
        last_trade_id = fetch_last_trade_id(es_client, index_name, market.symbol)
        logging.info(
            f"Public Trade Result Generator : Fetching Trades : Market Symbol {market.symbol} : Last Trade ID {last_trade_id} : Limit {limit}"
        )
        market_counter = 0
        min_trade_id = 1000000000
        max_trade_id = 0

        for trade in exchange.api(exchange).generate_public_trades(
            market.symbol, before=last_trade_id, limit=limit
        ):
            task_counter += 1
            market_counter += 1
            if task_counter > task_limit:
                logging.info(
                    f"Public Trade Result Generator : Reached Task Limit : Limit {task_limit} : Market Counters {market_counters}"
                )
                return
            if trade.trade_id > max_trade_id:
                max_trade_id = trade.trade_id
            if trade.trade_id < min_trade_id:
                min_trade_id = trade.trade_id
            yield trade.dict(by_alias=True)
        market_counters.update({market.symbol: market_counter})
        logging.info(
            f"Public Trade Result Generator : Market Completed : Symbol {market.symbol} : Min Trade ID {min_trade_id} : Max Trade ID {max_trade_id}"
        )
    logging.info(
        f"Public Trade Result Generator : All Markets Completed : Market Counters {market_counters}"
    )

import logging

from core.feeds.bittrex.helpers import fetch_markets


def bittrex_public_trade_result_generator(configs: dict, **kwargs):
    exchange_id_config_name = "exchange_id"
    exchange_id = configs.get(exchange_id_config_name)
    if not exchange_id:
        logging.error(
            f"Bittrex Trade Result Generator : Required Config key '{exchange_id_config_name}' is Missing or None"
        )
        return
    feed_data = fetch_markets(exchange_id)
    exchange = feed_data.get("exchange")
    if not exchange:
        logging.error(f"Bittrex Trade Result Generator : Exchange is Missing or None")
        return
    markets = feed_data.get("markets")
    if not markets:
        logging.error(f"Bittrex Trade Result Generator : Markets are Missing or None")
        return
    task_limit = configs.get("task_limit")
    if not task_limit:
        logging.error(
            f"Bittrex Trade Result Generator : Required Config key 'task_limit' is Missing or None"
        )
        return
    task_counter = 0
    market_counter = 0
    market_counters = {}
    for market in markets:
        snapshot = exchange.api(exchange).get_trade_sequence(market.symbol)
        if not snapshot:
            logging.error(
                "Bittrex Trade Result Generator : Trade Sequence is Invalid or None"
            )
            continue
        logging.info(
            f"Bittrex Trade Result Generator : Fetching Trades : Market Symbol {market.symbol} : Total Trades this Task {task_counter}"
        )
        if task_counter > task_limit:
            logging.info(
                f"Bittrex Trade Result Generator : Reached Task Limit : Limit {task_limit}"
            )
            return
        market_counter = 0
        for trade in exchange.api(exchange).generate_public_trades(market.symbol):
            task_counter += 1
            market_counter += 1
            trade.snapshot = snapshot
            yield trade.dict(by_alias=True)
        logging.info(
            f"Bittrex Trade Result Generator : Market Completed : Market Symbol {market.symbol} : Total Trades on Market {market_counter} : Total Trades this Task {task_counter}"
        )
        market_counters.update({market.symbol: market_counter})
    logging.info(
        f"Bittrex Trade Result Generator : All Markets Completed : Market Counters {market_counters}"
    )
    return

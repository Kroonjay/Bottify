import asyncio
import logging

from core.feeds.bittrex.helpers import fetch_markets


def bittrex_ticker_result_generator(configs: dict):
    exchange_id_config_name = "exchange_id"
    exchange_id = configs.get(exchange_id_config_name)
    if not exchange_id:
        logging.error(
            f"Bittrex Ticker Result Generator : Required Config key '{exchange_id_config_name}' is Missing or None"
        )
        return
    feed_data = fetch_markets(exchange_id)
    exchange = feed_data.get("exchange")
    if not exchange:
        logging.error(f"Bittrex Ticker Result Generator : Exchange is Missing or None")
        return
    markets = feed_data.get("markets")
    if not markets:
        logging.error(f"Bittrex Ticker Result Generator : Markets are Missing or None")
        return
    snapshot = exchange.api(exchange).get_ticker_sequence()
    if not snapshot:
        logging.error(
            "Bittrex Ticker Result Generator : Ticker Sequence is Invalid or None"
        )
        return
    ticker_count = 0
    for market in markets:
        ticker = exchange.api(exchange).get_ticker(market.symbol)
        if not ticker:
            logging.error(
                f"Bittrex Ticker Result Generator : Ticker is None : Market Symbol {market.symbol}"
            )
            continue
        ticker.snapshot = snapshot
        ticker_count += 1
        yield ticker.dict(by_alias=True)
    logging.info(
        f"Bittrex Ticker Result Generator : Complete : Total Tickers {ticker_count}"
    )

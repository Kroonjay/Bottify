from enum import Enum
import logging
from core.enums.feed_sources import FeedSources
from core.feeds.coinmarketcap.currency_info_feed import cmc_currency_result_generator
from core.feeds.coinbase.public_trades_feed import (
    coinbase_public_trade_result_generator,
)
from core.feeds.coinbase.daily_currency_stats_feed import (
    daily_currency_stats_result_generator,
)
from core.feeds.bittrex.public_trades_feed import bittrex_public_trade_result_generator
from core.feeds.bittrex.tickers_feed import bittrex_ticker_result_generator
from core.feeds.exchange.candles_feed import candle_result_generator

feed_result_generators = {
    FeedSources.CoinMarketCapCurrencyInfo: cmc_currency_result_generator,
    FeedSources.CoinbaseTrades: coinbase_public_trade_result_generator,
    FeedSources.CoinbaseDailyCurrencyStats: daily_currency_stats_result_generator,
    FeedSources.BittrexTrades: bittrex_public_trade_result_generator,
    FeedSources.BittrexTickers: bittrex_ticker_result_generator,
    FeedSources.Candles: candle_result_generator,
}


def get_feed_result_generator(feed_type: FeedSources):
    if not feed_type in feed_result_generators:
        logging.error(
            f"Failed to Load Feed Result Generator:Invalid Feed Type:Feed Type: {feed_type}"
        )
        return None
    return feed_result_generators.get(feed_type)

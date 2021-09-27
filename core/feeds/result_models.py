import logging
from core.enums.feed_sources import FeedSources
from core.exchanges.coinbase.models import (
    CoinbasePublicTradeModel,
    CoinbaseDailyCurrencyStatModel,
    CoinbaseSocketTickerModel,
)
from core.feeds.coinmarketcap.currency_info_feed import CoinMarketCapCurrencyInfoModel
from core.exchanges.bittrex.models import BittrexPublicTradeModel, BittrexTickerModel
from core.models.candle import CandleModel

feed_result_models = {
    FeedSources.CoinMarketCapCurrencyInfo: CoinMarketCapCurrencyInfoModel,
    FeedSources.CoinbaseTrades: CoinbasePublicTradeModel,
    FeedSources.CoinbaseDailyCurrencyStats: CoinbaseDailyCurrencyStatModel,
    FeedSources.CoinbaseTickers: CoinbaseSocketTickerModel,
    FeedSources.BittrexTrades: BittrexPublicTradeModel,
    FeedSources.BittrexTickers: BittrexTickerModel,
    FeedSources.Candles: CandleModel,
}


def get_feed_result_model(feed_type: FeedSources):
    if not feed_type in feed_result_models:
        logging.error(
            f"Failed to Load Feed Result Model : Invalid Feed Type : Feed Type: {feed_type}"
        )
        return None
    return feed_result_models.get(feed_type)

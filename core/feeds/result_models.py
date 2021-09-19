import logging
from core.enums.feed_sources import FeedSources
from core.exchanges.coinbase.models import (
    CoinbasePublicTradeModel,
    CoinbaseDailyCurrencyStatModel,
)
from core.feeds.coinmarketcap.currency_info_feed import CoinMarketCapCurrencyInfoModel

feed_result_models = {
    FeedSources.CoinMarketCapCurrencyInfo: CoinMarketCapCurrencyInfoModel,
    FeedSources.CoinbaseTrades: CoinbasePublicTradeModel,
    FeedSources.CoinbaseDailyCurrencyStats: CoinbaseDailyCurrencyStatModel,
}


def get_feed_result_model(feed_type: FeedSources):
    if not feed_type in feed_result_models:
        logging.error(
            f"Failed to Load Feed Result Model : Invalid Feed Type : Feed Type: {feed_type}"
        )
        return None
    return feed_result_models.get(feed_type)

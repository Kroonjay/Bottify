from enum import Enum


class FeedConfig(Enum):
    ExchangeID = "exchange_id"
    ExchangeIDs = "exchange_ids"
    MarketTags = "market_tags"
    MarketSymbol = "market_symbol"
    StartAt = "start_at"
    CandleLength = "candle_length"
    NewestCandle = "newest_candle_search_template"
    MaxResults = "max_results"
    MaxResultsPerMarket = "max_results_per_market"

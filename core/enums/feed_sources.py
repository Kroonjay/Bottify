from enum import IntEnum


class FeedSources(IntEnum):
    Reserved = 0
    CoinMarketCapCurrencyInfo = 100
    CoinbaseTrades = 200
    CoinbaseDailyCurrencyStats = 201
    BittrexTrades = 300
    BittrexDailyCurrencyStats = 301
    BittrexTickers = 302

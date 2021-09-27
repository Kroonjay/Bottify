from enum import IntEnum


class FeedSources(IntEnum):
    Reserved = 0
    Candles = 1
    CoinMarketCapCurrencyInfo = 100
    CoinbaseTrades = 200
    CoinbaseDailyCurrencyStats = 201
    CoinbaseTickers = 202
    BittrexTrades = 300
    BittrexDailyCurrencyStats = 301
    BittrexTickers = 302

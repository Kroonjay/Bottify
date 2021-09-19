from enum import Enum


class OrderDirection(Enum):
    Unset = 0
    Buy = 1
    Sell = 2


class OrderType(Enum):
    Unset = 0
    Limit = 1  # Should be supported everywhere
    Market = 2  # Should be supported everywhere
    CeilingLimit = 3  # Supported on Bittrex
    CeilingMarket = 4  # Supported on Bittrex


class OrderTimeInForce(Enum):
    Unset = 0
    GoodTilCancelled = 1  # Supported on Bittrex, Coinbase
    GoodTilTime = 2  # Supported on Coinbase
    ImmediateOrCancel = 3  # Supported on Bittrex, Coinbase
    FillOrKill = 4  # Supported on Bittrex, Coinbase
    PostOnlyGoodTilCancelled = 5  # Supported on Bittrex, Coinbase.  Order TYpe on Bittrex but Order Param for Limit order on Coinbase
    BuyNow = 6  # Supported on Bittrex
    Instant = 7  # Supported on Bittrex

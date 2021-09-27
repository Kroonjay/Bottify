from enum import Enum


# Any modifications to any of these enums must also be updated in the relevant Map in maps.py!
class CoinbaseOrderDirection(Enum):
    Buy = "buy"
    Sell = "sell"


class CoinbaseOrderType(Enum):
    Market = "market"
    Limit = "limit"


class CoinbaseOrderStop(Enum):
    Loss = "loss"
    Entry = "entry"


class CoinbaseTimeInForce(Enum):
    GoodTilCancelled = "GTC"
    GoodTilTime = "GTT"
    ImmediateOrCancel = "IOC"
    FillOrKill = "FOK"


class CoinbaseCancelAfter(Enum):
    OneMinute = "min"
    OneHour = "hour"
    OneDay = "day"


class CoinbaseMarketStatus(Enum):
    Active = "online"
    Disabled = "offline"
    Delisted = "delisted"


class CoinbaseOrderStatus(Enum):
    Open = "open"
    Pending = "pending"
    Active = "active"
    Closed = "done"
    All = "all"


class CoinbaseCandleLength(Enum):
    OneMinute = 60
    FiveMinutes = 300
    FifteenMinutes = 900
    OneHour = 3600
    SixHours = 21600
    OneDay = 86400

from enum import Enum


# Any modifications to any of these enums must also be updated in the relevant Map in maps.py!
class BittrexOrderDirection(Enum):
    Buy = "BUY"
    Sell = "SELL"


class BittrexOrderType(Enum):
    Market = "MARKET"
    Limit = "LIMIT"
    CeilingMarket = "CEILING_MARKET"
    CeilingLimit = "CEILING_LIMIT"


class BittrexTimeInForce(Enum):
    GoodTilCancelled = "GOOD_TIL_CANCELLED"
    ImmediateOrCancel = "IMMEDIATE_OR_CANCEL"
    FillOrKill = "FILL_OR_KILL"
    PostOnlyGoodTilCancelled = "POST_ONLY_GOOD_TIL_CANCELLED"
    BuyNow = "BUY_NOW"
    Instant = "INSTANT"


class BittrexOrderStatus(Enum):
    Open = "OPEN"
    Closed = "CLOSED"


class BittrexMarketStatus(Enum):
    Active = "ONLINE"
    Disabled = "OFFLINE"


class BittrexCandleLength(Enum):
    OneMinute = "MINUTE_1"
    FiveMinutes = "MINUTE_5"
    OneHour = "HOUR_1"
    OneDay = "DAY_1"

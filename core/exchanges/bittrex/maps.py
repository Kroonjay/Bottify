import logging
from core.enums.candle_length import CandleLength
from core.enums.orders import OrderDirection, OrderTimeInForce, OrderType
from core.exchanges.bittrex.enums import (
    BittrexOrderDirection,
    BittrexOrderType,
    BittrexTimeInForce,
    BittrexCandleLength,
)

order_direction_map = {
    OrderDirection.Buy: BittrexOrderDirection.Buy,
    OrderDirection.Sell: BittrexOrderDirection.Sell,
}

order_type_map = {
    OrderType.Market: BittrexOrderType.Market,
    OrderType.Limit: BittrexOrderType.Limit,
    OrderType.CeilingLimit: BittrexOrderType.CeilingLimit,
    OrderType.CeilingMarket: BittrexOrderType.CeilingMarket,
}

time_in_force_map = {
    OrderTimeInForce.GoodTilCancelled: BittrexTimeInForce.GoodTilCancelled,
    OrderTimeInForce.ImmediateOrCancel: BittrexTimeInForce.ImmediateOrCancel,
    OrderTimeInForce.FillOrKill: BittrexTimeInForce.FillOrKill,
    OrderTimeInForce.PostOnlyGoodTilCancelled: BittrexTimeInForce.PostOnlyGoodTilCancelled,
    OrderTimeInForce.BuyNow: BittrexTimeInForce.BuyNow,
    OrderTimeInForce.Instant: BittrexTimeInForce.Instant,
}

candle_length_map = {
    CandleLength.OneMinute: BittrexCandleLength.OneMinute,
    CandleLength.FiveMinutes: BittrexCandleLength.FiveMinutes,
    CandleLength.OneHour: BittrexCandleLength.OneHour,
    CandleLength.OneDay: BittrexCandleLength.OneDay,
}


def map_bittrex_order_direction(order_direction: OrderDirection):
    if not isinstance(order_direction, OrderDirection):
        logging.error(
            f"Map Bittrex Order Direction : Input Must be an OrderDirection Enum : Got {type(order_direction)}"
        )
        return None
    return order_direction_map.get(order_direction)


def map_bittrex_order_type(order_type: OrderType):
    if not isinstance(order_type, OrderType):
        logging.error(
            f"Map Bittrex Order Type : Input Must be an OrderType Enum : Got {type(order_type)}"
        )
        return None
    return order_type_map.get(order_type)


def map_bittrex_time_in_force(time_in_force: OrderTimeInForce):
    if not isinstance(time_in_force, OrderTimeInForce):
        logging.error(
            f"Map Bittrex Order Time in Force : Input Must be an OrderTimeInForce Enum : Got {type(time_in_force)}"
        )
        return None
    return time_in_force_map.get(time_in_force)


def map_bittrex_candle_length(candle_length: CandleLength):
    default_candle_length = BittrexCandleLength.OneHour
    if not isinstance(candle_length, CandleLength):
        logging.error(
            f"Map Bittrex Candle Length : Input Must be a CandleLength Enum : Got {type(candle_length)}"
        )
        return None
    candle_length = candle_length_map.get(candle_length)
    if candle_length:
        return candle_length
    else:
        logging.error(
            f"Map Bittrex Candle Length : Candle Length {str(candle_length)} Not Supported on Bittrex : Using Default {default_candle_length}"
        )
        return default_candle_length

import logging
from core.enums.statuses import BottifyStatus
from core.enums.orders import OrderDirection, OrderTimeInForce, OrderType
from core.exchanges.coinbase.enums import (
    CoinbaseOrderDirection,
    CoinbaseOrderType,
    CoinbaseTimeInForce,
    CoinbaseOrderStatus,
)

order_direction_map = {
    OrderDirection.Buy: CoinbaseOrderDirection.Buy,
    OrderDirection.Sell: CoinbaseOrderDirection.Sell,
}

order_type_map = {
    OrderType.Market: CoinbaseOrderType.Market,
    OrderType.Limit: CoinbaseOrderType.Limit,
}

time_in_force_map = {
    OrderTimeInForce.GoodTilCancelled: CoinbaseTimeInForce.GoodTilCancelled,
    OrderTimeInForce.ImmediateOrCancel: CoinbaseTimeInForce.ImmediateOrCancel,
    OrderTimeInForce.FillOrKill: CoinbaseTimeInForce.FillOrKill,
    OrderTimeInForce.GoodTilTime: CoinbaseTimeInForce.GoodTilTime,
}

order_status_map = {
    BottifyStatus.Active: CoinbaseOrderStatus.Open,
    BottifyStatus.New: CoinbaseOrderStatus.Pending,
    BottifyStatus.Complete: CoinbaseOrderStatus.Closed,
}


def map_coinbase_order_direction(order_direction: OrderDirection):
    if isinstance(order_direction, OrderDirection):
        return order_direction_map.get(order_direction)
    elif isinstance(order_direction, CoinbaseOrderDirection):
        for key, value in order_direction_map.items():
            if value == order_direction:
                return key
        logging.error(
            f"Map Coinbase Order Direction : No Valid Key for Value : Value {order_direction}"
        )
    logging.error("Map Coinbase Order Direction : Invalid Input")
    return None


def map_coinbase_order_type(order_type: OrderType):
    if isinstance(order_type, OrderType):
        return order_type_map.get(order_type)
    elif isinstance(order_type, CoinbaseOrderType):
        for key, value in order_type_map.items():
            if value == order_type:
                return key
        logging.error(
            f"Map Coinbase Order Type : No Valid Key for Value : Value {order_type}"
        )
    logging.error("Map Coinbase Order Type : Invalid Input")
    return None


def map_coinbase_time_in_force(time_in_force):
    if isinstance(time_in_force, OrderTimeInForce):
        return time_in_force_map.get(time_in_force)
    elif isinstance(time_in_force, CoinbaseTimeInForce):
        for key, value in time_in_force_map.items():
            if value == time_in_force:
                return key
        logging.error(
            f"Map Coinbase Order Time In Force : No Valid Key for Value : Value {time_in_force}"
        )
    # logging.error("Map Coinbase Order Time in Force : Invalid Input")
    return OrderTimeInForce.Unset


def map_coinbase_order_status(order_status):
    if isinstance(order_status, BottifyStatus):
        return time_in_force_map.get(order_status)
    elif isinstance(order_status, CoinbaseOrderStatus):
        for key, value in order_status_map.items():
            if value == order_status:
                return key
        logging.error(
            f"Map Coinbase Order Status : No Valid Key for Value : Value {order_status}"
        )
    logging.error("Map Coinbase Order Status : Invalid Input")
    return None

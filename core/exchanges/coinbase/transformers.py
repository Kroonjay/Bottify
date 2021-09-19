from pydantic import ValidationError
import logging
from uuid import UUID
from decimal import Decimal
from core.exchanges.coinbase.models import (
    CoinbaseNewLimitOrderModel,
    CoinbaseNewMarketOrderModel,
    CoinbaseTradeModel,
    CoinbaseBalanceModel,
    CoinbaseMarketModel,
    CoinbaseOrderModel,
)
from core.models.trade import TradeInModel
from core.enums.exchanges import Exchange
from core.enums.statuses import BottifyStatus
from core.enums.orders import OrderType
from core.models.market import MarketInModel
from core.models.order import BottifyOrderCreateModel, BottifyOrderInModel
from core.models.balance import CurrencyBalanceInModel
from core.exchanges.coinbase.enums import CoinbaseMarketStatus
from core.exchanges.coinbase.maps import (
    map_coinbase_order_direction,
    map_coinbase_order_type,
    map_coinbase_time_in_force,
    map_coinbase_order_status,
)

# Can't do this with validators because the attribute names are different
# Could probably do it with Fields and aliases but that's a lot of work and this is still pretty clean :/
def transform_order_create_to_coinbase(
    bottify_order_create: BottifyOrderCreateModel, market_symbol: str
):
    if bottify_order_create.order_type == OrderType.Limit:
        try:
            return CoinbaseNewLimitOrderModel(
                client_oid=bottify_order_create.order_guid,
                product_id=market_symbol,
                side=map_coinbase_order_direction(bottify_order_create.direction),
                type=map_coinbase_order_type(bottify_order_create.order_type),
                price=bottify_order_create.price,
                size=bottify_order_create.quantity,
                time_in_force=map_coinbase_time_in_force(
                    bottify_order_create.time_in_force
                )
                # TODO Build in support for stop conditions, stop & stop_price attrs currently unused
            )
        except ValidationError as ve:
            logging.error(
                f"Transform Order Coinbase : CoinbaseNewLimitOrderModel : ValidationError : {ve.json()}"
            )
            return None
    elif bottify_order_create.order_type == OrderType.Market:
        try:
            return CoinbaseNewMarketOrderModel(
                client_oid=bottify_order_create.order_guid,
                product_id=market_symbol,
                side=map_coinbase_order_direction(bottify_order_create.direction),
                type=map_coinbase_order_type(bottify_order_create.order_type),
                size=bottify_order_create.quantity,
            )
        except ValidationError as ve:
            logging.error(
                f"Transform Order Coinbase : CoinbaseNewMarketOrderModel : ValidationError : {ve.json()}"
            )
            return None
    else:
        logging.error(
            f"Transform Order Coinbase : Unsupported Order Type : Order Type {bottify_order_create.order_type}"
        )
        return None


def transform_coinbase_order(
    order_in: CoinbaseOrderModel, strategy_id: int, market_id: int, order_guid: UUID
):
    try:
        return BottifyOrderInModel(
            order_guid=order_guid,  # Coinbase won't return Client-generated Order ID's in this response, but you can query by client_id
            source_id=str(order_in.source_id),
            strategy_id=strategy_id,
            market_id=market_id,
            status=map_coinbase_order_status(order_in.status),
            direction=map_coinbase_order_direction(order_in.side),
            order_type=map_coinbase_order_type(order_in.type),
            price=order_in.price,
            quantity=order_in.size,
            time_in_force=map_coinbase_time_in_force(order_in.time_in_force),
            created_at=order_in.created_at,
        )
    except ValidationError as ve:
        logging.error(
            f"Transform Coinbase Order : BottifyOrderInModel : ValidationError : {ve.json()}"
        )
        return None


def transform_trade_coinbase(
    coinbase_trade_in: CoinbaseTradeModel, bottify_order_id: int
):
    try:
        return TradeInModel(
            source_id=coinbase_trade_in.trade_id,
            bottify_order_id=bottify_order_id,
            is_taker=False if coinbase_trade_in.liquidity == "M" else True,
            price=coinbase_trade_in.price,
            quantity=coinbase_trade_in.size,
            fee=coinbase_trade_in.fee,
            executed_at=coinbase_trade_in.created_at,
        )
    except ValidationError as ve:
        logging.error(f"Transform Trade Coinbase : ValidationError : {ve.json()}")
        return None


def transform_balance_coinbase(
    coinbase_balance: CoinbaseBalanceModel, currency_id: int, exchange_id: int
):
    try:
        return CurrencyBalanceInModel(
            currency_id=currency_id,
            exchange_id=exchange_id,
            available=coinbase_balance.available,
            reserved=coinbase_balance.hold,
        )
    except ValidationError as ve:
        logging.error(f"Transform Balance Coinbase : ValidationError : {ve.json()}")
        return None


def transform_market_coinbase(
    coinbase_market: CoinbaseMarketModel,
    exchange_id: int,
    base_currency_id: int,
    quote_currency_id: int,
) -> MarketInModel:
    if not isinstance(coinbase_market, CoinbaseMarketModel):
        logging.error(
            f"Transform Market Coinbase : Input Must be a CoinbaseMarketModel : Got {type(coinbase_market)}"
        )
        return None

    if coinbase_market.status == CoinbaseMarketStatus.Active:
        status = BottifyStatus.Active
    elif coinbase_market.status == CoinbaseMarketStatus.Disabled:
        status = BottifyStatus.SourceDisabled
    elif coinbase_market.status == CoinbaseMarketStatus.Delisted:
        status = BottifyStatus.SourceDeleted
    else:
        logging.error(
            f"Transform Market Conbase : Unrecognized Market Status : Got {coinbase_market.status}"
        )
        status = BottifyStatus.Unset
    try:
        return MarketInModel(
            base_currency_id=base_currency_id,
            quote_currency_id=quote_currency_id,
            exchange_id=exchange_id,
            symbol=coinbase_market.symbol,
            min_trade_size=coinbase_market.base_min_size,
            notice=coinbase_market.status_message,
            status=status,
        )
    except ValidationError as ve:
        logging.error(
            f"Transform Market Coinbase : MarketInModel : ValidationError : {ve.json()}"
        )
        return None

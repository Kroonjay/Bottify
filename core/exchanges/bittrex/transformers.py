from pydantic import ValidationError
import logging
from decimal import Decimal
from core.exchanges.bittrex.models import (
    BittrexNewOrderModel,
    BittrexTradeModel,
    BittrexBalanceModel,
    BittrexMarketModel,
)
import json
from core.enums.statuses import BottifyStatus
from core.models.trade import TradeInModel
from core.enums.exchanges import Exchange
from core.models.market import MarketInModel
from core.models.order import BottifyOrderCreateModel
from core.models.balance import CurrencyBalanceInModel
from core.exchanges.bittrex.enums import BittrexMarketStatus
from core.exchanges.bittrex.maps import (
    map_bittrex_order_direction,
    map_bittrex_order_type,
    map_bittrex_time_in_force,
)

# Can't do this with validators because the attribute names are different :/
def transform_order_bittrex(
    bottify_order_create: BottifyOrderCreateModel, market_symbol: str
):
    try:
        return BittrexNewOrderModel(
            marketSymbol=market_symbol,
            direction=map_bittrex_order_direction(bottify_order_create.direction),
            type=map_bittrex_order_type(bottify_order_create.order_type),
            quantity=bottify_order_create.quantity,
            limit=bottify_order_create.price,
            timeInForce=map_bittrex_time_in_force(bottify_order_create.time_in_force),
            clientOrderId=bottify_order_create.order_guid,
        )
    except ValidationError as ve:
        logging.error(f"Transform Order Bittrex : ValidationError : {ve.json()}")
        return None


def transform_trade_bittrex(bittrex_trade_in: BittrexTradeModel, bottify_order_id: int):
    try:
        return TradeInModel(
            source_id=bittrex_trade_in.id,
            bottify_order_id=bottify_order_id,
            is_taker=bittrex_trade_in.isTaker,
            price=bittrex_trade_in.rate,
            quantity=bittrex_trade_in.quantity,
            fee=bittrex_trade_in.commission,
            executed_at=bittrex_trade_in.executedAt,
        )
    except ValidationError as ve:
        logging.error(f"Transform Trade Bittrex : ValidationError : {ve.json()}")
        return None


def transform_balance_bittrex(
    bittrex_balance: BittrexBalanceModel, currency_id: int, exchange_id: int
) -> CurrencyBalanceInModel:
    try:
        return CurrencyBalanceInModel(
            currency_id=currency_id,
            exchange_id=exchange_id,
            available=bittrex_balance.available,
            reserved=bittrex_balance.total - bittrex_balance.available,
        )
    except ValidationError as ve:
        logging.error(f"Transform Balance Bittrex : ValidationError : {ve.json()}")
        return None


def transform_market_bittrex(
    bittrex_market: BittrexMarketModel,
    exchange_id: int,
    base_currency_id: int,
    quote_currency_id: int,
) -> MarketInModel:

    if not isinstance(bittrex_market, BittrexMarketModel):
        logging.error(
            f"Transform Market Bittrex : Input Must be a BittrexMarketModel : Got {type(bittrex_market)}"
        )
        return None
    if bittrex_market.tags:
        tags = json.dumps(bittrex_market.tags)
    else:
        tags = None
    if bittrex_market.status == BittrexMarketStatus.Active:
        status = BottifyStatus.Active
    elif bittrex_market.status == BittrexMarketStatus.Disabled:
        status = BottifyStatus.SourceDisabled
    else:
        logging.error(
            f"Transform Market Bittrex : Unrecognized Market Status : Got {bittrex_market.status}"
        )
        status = BottifyStatus.Unset
    try:
        return MarketInModel(
            base_currency_id=base_currency_id,
            quote_currency_id=quote_currency_id,
            exchange_id=exchange_id,
            symbol=bittrex_market.symbol,
            min_trade_size=bittrex_market.minTradeSize,
            notice=bittrex_market.notice,
            tags=tags,
            status=status,
        )
    except ValidationError as ve:
        logging.error(
            f"Transform Bittrex Market : MarketInModel : ValidationError : {ve.json()}"
        )
        return None

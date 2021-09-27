from pydantic import BaseModel, condecimal, Field, validator
from uuid import uuid4, UUID
from typing import Optional, List
from decimal import Decimal
from datetime import datetime, timezone
from core.enums.candle_length import CandleLength
from core.config import BALANCE_DECIMAL_PRECISION, BALANCE_MAXIMUM_DIGITS
from core.exchanges.coinbase.enums import (
    CoinbaseOrderDirection,
    CoinbaseOrderType,
    CoinbaseTimeInForce,
    CoinbaseOrderStop,
    CoinbaseCancelAfter,
    CoinbaseMarketStatus,
    CoinbaseOrderStatus,
)


# Values are set to None so we can exclude them via exclude_none but we can still use some helpful defaults
class CoinbaseNewOrderModel(BaseModel):
    client_oid: UUID
    product_id: str  # Market Slug ex. BTC-USD
    side: CoinbaseOrderDirection
    type: CoinbaseOrderType
    stop: Optional[CoinbaseOrderStop] = None
    stop_price: Optional[
        condecimal(
            ge=0,
            lt=100000000,
            max_digits=BALANCE_MAXIMUM_DIGITS,
            decimal_places=BALANCE_DECIMAL_PRECISION,
        )
    ] = None

    class Config:
        use_enum_values = True


class CoinbaseNewLimitOrderModel(CoinbaseNewOrderModel):
    price: condecimal(
        ge=0,
        lt=100000000,
        max_digits=BALANCE_MAXIMUM_DIGITS,
        decimal_places=BALANCE_DECIMAL_PRECISION,
    )
    size: condecimal(
        ge=0,
        lt=100000000,
        max_digits=BALANCE_MAXIMUM_DIGITS,
        decimal_places=BALANCE_DECIMAL_PRECISION,
    )
    time_in_force: CoinbaseTimeInForce = CoinbaseTimeInForce.GoodTilCancelled
    cancel_after: Optional[CoinbaseCancelAfter] = None
    post_only: Optional[bool] = None

    class Config:
        use_enum_values = True


class CoinbaseNewMarketOrderModel(CoinbaseNewOrderModel):
    size: Optional[
        condecimal(
            ge=0,
            lt=100000000,
            max_digits=BALANCE_MAXIMUM_DIGITS,
            decimal_places=BALANCE_DECIMAL_PRECISION,
        )
    ] = None
    funds: Optional[
        condecimal(
            ge=0,
            lt=100000000,
            max_digits=BALANCE_MAXIMUM_DIGITS,
            decimal_places=BALANCE_DECIMAL_PRECISION,
        )
    ] = None


class CoinbaseOrderModel(BaseModel):
    source_id: UUID = Field(alias="id")
    price: Optional[Decimal] = None
    size: Decimal
    market_symbol: str = Field(alias="product_id")
    side: CoinbaseOrderDirection
    stp: Optional[str] = None
    type: CoinbaseOrderType
    time_in_force: Optional[CoinbaseTimeInForce] = None
    post_only: bool
    created_at: datetime
    done_at: Optional[datetime] = None
    done_reason: Optional[str] = None
    fill_fees: Decimal
    filled_size: Decimal
    executed_value: Decimal
    status: CoinbaseOrderStatus
    settled: bool


class CoinbaseTradeModel(BaseModel):
    trade_id: int
    order_id: UUID
    product_id: str
    price: Decimal
    size: Decimal
    created_at: datetime
    liquidity: str
    fee: Decimal
    settled: bool
    side: str


class CoinbaseBalanceModel(BaseModel):
    id: UUID
    symbol: str = Field(
        alias="currency"
    )  # This is required for the async_work_update_exchange_balances task to be able to retrieve currency rows using a common attribute name
    balance: Decimal
    hold: Decimal
    available: Decimal
    trading_enabled: bool


class CoinbaseMarketModel(BaseModel):
    symbol: str = Field(alias="id")
    display_name: str = None
    base_currency_symbol: str = Field(alias="base_currency")
    quote_currency_symbol: str = Field(alias="quote_currency")
    base_increment: Decimal
    quote_increment: Decimal
    base_min_size: Decimal
    base_max_size: Decimal
    min_market_funds: Decimal
    max_market_funds: Decimal
    status: CoinbaseMarketStatus
    status_message: Optional[str] = None
    cancel_only: bool
    limit_only: bool
    post_only: bool
    trading_disabled: bool
    fx_stablecoin: bool


class CoinbaseApiTickerModel(BaseModel):
    trade_id: int
    price: Decimal
    size: Decimal
    bid: Decimal
    ask: Decimal
    volume: Decimal
    time: datetime


class CoinbaseSocketTickerModel(BaseModel):
    sequence: str
    product_id: str = Field(alias="market_symbol")
    price: Decimal
    open_24h: Decimal
    volume_24h: Decimal
    low_24h: Decimal
    high_24h: Decimal
    volume_30d: Decimal
    best_bid: Decimal = Field(
        alias="bid"
    )  # Required for commonality with other exchanges
    best_ask: Decimal = Field(alias="ask")
    side: str
    time: datetime
    trade_id: int
    last_size: Decimal

    class Config:
        extra = "ignore"
        allow_population_by_field_name = True


class CoinbaseSocketFeederConfig(BaseModel):
    exchange_id: int
    channels: List[str]
    socket_url: str
    products: Optional[List[str]] = None
    ticker_index_name: str = None
    max_retries: int = 10


class CoinbasePublicTradeModel(BaseModel):
    trade_id: int
    market_symbol: str
    time: datetime
    price: Decimal
    size: Decimal
    side: str
    id: str = Field(alias="_id", default=None)

    class Config:
        allow_population_by_field_name = True
        extra = "ignore"

    @validator(
        "id", always=True
    )  # Required because Trade ID's aren't unique across products on Coinbase :/
    def set_id(cls, v, values, **kwargs):
        assert values.get("market_symbol"), f"Market Symbol is Required"
        assert values.get("trade_id"), f"Trade ID is Required"
        return f"{values.get('market_symbol')}-{values.get('trade_id')}"


class CoinbaseDailyCurrencyStatModel(BaseModel):
    open: Decimal
    high: Decimal
    low: Decimal
    volume: Decimal
    last: Decimal
    volume_30d: Decimal = Field(alias="volume_30day")


class CoinbaseCandleModel(BaseModel):
    exchange_id: int
    market_symbol: str
    length: CandleLength
    low: Decimal
    high: Decimal
    open: Decimal
    close: Decimal
    volume: Decimal
    time: datetime

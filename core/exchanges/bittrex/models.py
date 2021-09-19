from pydantic import BaseModel, condecimal, Field
from uuid import uuid4, UUID
from typing import Optional, List
from decimal import Decimal
from datetime import datetime, timezone
from core.config import BALANCE_DECIMAL_PRECISION, BALANCE_MAXIMUM_DIGITS
from core.exchanges.bittrex.enums import (
    BittrexOrderDirection,
    BittrexOrderType,
    BittrexTimeInForce,
    BittrexMarketStatus,
    BittrexOrderStatus,
)


class BittrexNewOrderModel(BaseModel):
    marketSymbol: str
    direction: BittrexOrderDirection
    type: str = BittrexOrderType
    quantity: Optional[
        condecimal(
            ge=0,
            lt=100000000,
            max_digits=BALANCE_MAXIMUM_DIGITS,
            decimal_places=BALANCE_DECIMAL_PRECISION,
        )
    ] = 0
    ceiling: Optional[
        condecimal(
            ge=0,
            lt=100000000,
            max_digits=BALANCE_MAXIMUM_DIGITS,
            decimal_places=BALANCE_DECIMAL_PRECISION,
        )
    ] = 0
    limit: Optional[
        condecimal(
            ge=0,
            lt=100000000,
            max_digits=BALANCE_MAXIMUM_DIGITS,
            decimal_places=BALANCE_DECIMAL_PRECISION,
        )
    ] = 0
    timeInForce: BittrexTimeInForce
    clientOrderId: UUID = uuid4()
    useAwards: Optional[bool] = False

    class Config:
        use_enum_values = True


class BittrexOrderModel(BaseModel):
    id: UUID
    marketSymbol: str
    direction: BittrexOrderDirection
    type: BittrexOrderType
    quantity: Optional[Decimal]
    limit: Optional[Decimal]
    ceiling: Optional[Decimal]
    timeInForce: BittrexTimeInForce
    clientOrderId: UUID
    fillQuantity: Decimal
    commission: Decimal
    proceeds: Decimal
    status: BittrexOrderStatus
    createdAt: datetime
    updatedAt: datetime
    closedAt: datetime

    class Config:
        extra = "ignore"


class BittrexTradeModel(BaseModel):
    id: UUID
    marketSymbol: str
    executedAt: datetime
    quantity: Decimal
    rate: Decimal
    orderId: UUID
    commission: Decimal
    isTaker: bool


class BittrexBalanceModel(BaseModel):
    symbol: str = Field(
        alias="currencySymbol"
    )  # This is required for the async_work_update_exchange_balances task to be able to retrieve currency rows using a common attribute name
    total: Decimal
    available: Decimal
    updatedAt: datetime


class BittrexMarketModel(BaseModel):
    symbol: str  # This doesn't require an alias because both Bittrex and Bottify use "symbol" for attribute name
    base_currency_symbol: str = Field(
        alias="baseCurrencySymbol"
    )  # This is required for async_work_update_exchange_markets task to be able to retrieve currency rows using a common attribute name
    quote_currency_symbol: str = Field(alias="quoteCurrencySymbol")
    minTradeSize: Decimal
    precision: int
    status: BittrexMarketStatus
    createdAt: datetime
    notice: Optional[str] = None
    prohibitedIn: List[str] = None
    associatedTermsOfServie: List[str] = None
    tags: List[str]


class BittrexTickerModel(BaseModel):
    symbol: str
    price: Decimal = Field(alias="lastTradeRate")  # Just call it price ffs?
    bidRate: Decimal
    askRate: Decimal

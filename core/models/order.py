from pydantic import BaseModel, validator, condecimal
from decimal import Decimal
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Optional
from core.enums.statuses import BottifyStatus
from core.enums.orders import OrderDirection, OrderTimeInForce, OrderType
from core.config import settings
from core.models.balance import round_decimal


class BottifyOrderCreateModel(BaseModel):
    order_guid: UUID = None  # Bottify-Generated Order ID
    strategy_id: int
    market_id: int
    direction: OrderDirection
    order_type: OrderType
    price: Optional[
        condecimal(
            ge=0,
            lt=100000000,
            max_digits=settings.BalanceMaximumDigits,
            decimal_places=settings.BalanceDecimalPrecision,
        )
    ] = 0  # Price is only relevant for limit orders
    quantity: condecimal(
        ge=0,
        lt=100000000,
        max_digits=settings.BalanceMaximumDigits,
        decimal_places=settings.BalanceDecimalPrecision,
    ) = 0
    time_in_force: OrderTimeInForce = OrderTimeInForce.GoodTilCancelled

    @validator("order_guid", pre=True, always=True)
    def set_order_guid(cls, v):
        return uuid4()

    @validator("price", "quantity", pre=True)
    def validate_decimals(cls, v):
        if not v:
            v = 0
        return round_decimal(v)

    @validator("time_in_force", pre=True)
    def set_time_in_force(cls, v):
        if not v:  # Not totally sure why this is required...but it is
            return OrderTimeInForce.GoodTilCancelled
        else:
            return v

    class Config:
        validate_assignment = True


# No reason for these fields to be required in Create object, but required for DB.  Main purpose of this class is to convert enums to their values
class BottifyOrderInModel(BottifyOrderCreateModel):
    source_id: str  # Order ID on the Exchange the order was placed
    status: BottifyStatus = BottifyStatus.Unset
    created_at: datetime = datetime.now(tz=timezone.utc)
    updated_at: datetime = datetime.now(tz=timezone.utc)

    class Config:
        use_enum_values = True


class BottifyOrderModel(BottifyOrderCreateModel):
    id: int
    source_id: str
    status: BottifyStatus
    created_at: datetime
    updated_at: datetime

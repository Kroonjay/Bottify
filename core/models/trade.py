from pydantic import BaseModel, validator, condecimal
from datetime import datetime, timezone

from core.config import BALANCE_DECIMAL_PRECISION, BALANCE_MAXIMUM_DIGITS
from core.models.balance import round_decimal


class TradeInModel(BaseModel):
    source_id: str
    bottify_order_id: int
    is_taker: bool
    price: condecimal(
        ge=0,
        lt=100000000,
        max_digits=BALANCE_MAXIMUM_DIGITS,
        decimal_places=BALANCE_DECIMAL_PRECISION,
    ) = 0  # Amount of currency we spent (Credit)
    quantity: condecimal(
        ge=0,
        lt=100000000,
        max_digits=BALANCE_MAXIMUM_DIGITS,
        decimal_places=BALANCE_DECIMAL_PRECISION,
    ) = 0  # Amount of currency we received (Debit)
    fee: condecimal(
        ge=0,
        lt=100000000,
        max_digits=BALANCE_MAXIMUM_DIGITS,
        decimal_places=BALANCE_DECIMAL_PRECISION,
    ) = 0
    executed_at: datetime
    created_at: datetime = datetime.now(tz=timezone.utc)

    @validator("price", "quantity", "fee", pre=True)
    def validate_decimals(cls, v):
        return round_decimal(v)


class TradeModel(TradeInModel):
    id: int

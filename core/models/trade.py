from pydantic import BaseModel, validator, condecimal
from datetime import datetime, timezone

from core.config import settings
from core.models.balance import round_decimal


class TradeInModel(BaseModel):
    source_id: str
    bottify_order_id: int
    is_taker: bool
    price: condecimal(
        ge=0,
        lt=100000000,
        max_digits=settings.BalanceMaximumDigits,
        decimal_places=settings.BalanceDecimalPrecision,
    ) = 0  # Amount of currency we spent (Credit)
    quantity: condecimal(
        ge=0,
        lt=100000000,
        max_digits=settings.BalanceMaximumDigits,
        decimal_places=settings.BalanceDecimalPrecision,
    ) = 0  # Amount of currency we received (Debit)
    fee: condecimal(
        ge=0,
        lt=100000000,
        max_digits=settings.BalanceMaximumDigits,
        decimal_places=settings.BalanceDecimalPrecision,
    ) = 0
    executed_at: datetime
    created_at: datetime = datetime.now(tz=timezone.utc)

    @validator("price", "quantity", "fee", pre=True)
    def validate_decimals(cls, v):
        return round_decimal(v)


class TradeModel(TradeInModel):
    id: int

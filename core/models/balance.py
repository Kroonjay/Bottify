from pydantic import BaseModel, validator, condecimal
from datetime import datetime, timezone
from core.config import settings
from core.enums.exchanges import Exchange
from decimal import Decimal, ROUND_DOWN
import math


# Simple Truncation function, taken from https://stackoverflow.com/questions/8595973/truncate-to-three-decimals-in-python
def truncate(number, decimals=0):
    """
    Returns a value truncated to a specific number of decimal places.
    """
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer.")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more.")
    elif decimals == 0:
        return math.trunc(number)

    factor = 10.0 ** decimals
    return math.trunc(number * factor) / factor


def round_decimal(number, decimal_places=settings.BalanceDecimalPrecision):
    if isinstance(number, Decimal):
        decimal_value = number
    else:
        decimal_value = Decimal(number)
    return decimal_value.quantize(Decimal(10) ** -decimal_places)


class CurrencyBalanceInModel(BaseModel):
    currency_id: int
    exchange_id: int
    available: condecimal(
        ge=0,
        lt=100000000,  # Maximum balance must be under 100 Million (8 digits) in order to maintain 8 decimal places
        max_digits=settings.BalanceMaximumDigits,
        decimal_places=settings.BalanceDecimalPrecision,
    ) = 0  # Must be greater than or equal to 0, maximum of 32 total digits not including trailing 0's, maximum decimal precision of 8
    reserved: condecimal(
        ge=0,
        lt=100000000,
        max_digits=settings.BalanceMaximumDigits,
        decimal_places=settings.BalanceDecimalPrecision,
    ) = 0  # Must be greater than or equal to 0, maximum of 32 total digits not including trailing 0's, maximum decimal precision of 8 = 0
    updated_at: datetime = datetime.now(tz=timezone.utc)

    @validator("available", pre=True)
    def validate_available_balance(cls, v):
        return round_decimal(v)

    @validator("reserved", pre=True)
    def validate_reserved_balance(cls, v):
        return round_decimal(v)

    class Config:
        validate_assignment = True
        validate_all = True
        extra = "ignore"
        use_enum_values = True


class CurrencyBalanceModel(CurrencyBalanceInModel):
    id: int
    updated_at: datetime
    total: condecimal(
        ge=0,
        lt=100000000,
        max_digits=settings.BalanceMaximumDigits,
        decimal_places=settings.BalanceDecimalPrecision,
    )

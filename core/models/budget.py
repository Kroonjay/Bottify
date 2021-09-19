from pydantic import BaseModel, validator, condecimal
from core.config import BALANCE_DECIMAL_PRECISION, BALANCE_MAXIMUM_DIGITS
from datetime import datetime, timezone

# Basically balances, but they are restricted to a given strategy.  We manage the accounting, whereas exchanges manage balances.
class BudgetInModel(BaseModel):
    currency_id: int
    exchange_id: int
    strategy_id: int
    available: condecimal(
        ge=0,
        lt=100000000,  # Maximum balance must be under 100 Million (8 digits) in order to maintain 8 decimal places
        max_digits=BALANCE_MAXIMUM_DIGITS,
        decimal_places=BALANCE_DECIMAL_PRECISION,
    ) = 0  # Must be greater than or equal to 0, maximum of 32 total digits not including trailing 0's, maximum decimal precision of 8
    reserved: condecimal(
        ge=0,
        lt=100000000,
        max_digits=BALANCE_MAXIMUM_DIGITS,
        decimal_places=BALANCE_DECIMAL_PRECISION,
    ) = 0  # Must be greater than or equal to 0, maximum of 32 total digits not including trailing 0's, maximum decimal precision of 8 = 0
    updated_at: datetime = datetime.now(tz=timezone.utc)

    # Not sure if we should be using round_decimal validator here.  Hoping it isn't required...


class BudgetModel(BudgetInModel):
    id: int
    total: condecimal(
        ge=0,
        lt=100000000,
        max_digits=BALANCE_MAXIMUM_DIGITS,
        decimal_places=BALANCE_DECIMAL_PRECISION,
    ) = 0

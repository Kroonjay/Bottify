from enum import IntEnum


class BudgetResult(IntEnum):
    Unset = 0
    Success = 1
    InsufficientFunds = 2
    InvalidAmount = 3
    NoRecord = 4
    InvalidFunctionParameter = 5

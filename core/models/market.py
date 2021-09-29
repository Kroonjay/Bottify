import json
from pydantic import BaseModel, validator, condecimal
from datetime import datetime, timezone
from typing import Optional, List
from core.enums.statuses import BottifyStatus
from core.config import settings


class MarketCreateModel(BaseModel):
    base_currency_id: int
    quote_currency_id: int
    exchange_id: int
    symbol: str
    min_trade_size: condecimal(
        ge=0,
        lt=100000000,
        max_digits=settings.BalanceMaximumDigits,
        decimal_places=settings.BalanceDecimalPrecision,
    )
    tags: Optional[List[str]] = None


class MarketInModel(MarketCreateModel):
    status: BottifyStatus = BottifyStatus.Active
    notice: Optional[str] = None
    tags: Optional[str] = None
    created_at: datetime = datetime.now(tz=timezone.utc)
    updated_at: datetime = datetime.now(tz=timezone.utc)

    @validator("tags", pre=True)
    def dump_tags(cls, v):
        if isinstance(v, list):
            return json.dumps(v)
        elif isinstance(v, str):
            return v
        else:
            return None

    class Config:
        use_enum_values = True


class MarketModel(MarketCreateModel):
    id: int
    status: BottifyStatus
    notice: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @validator("tags", pre=True)
    def load_tags(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        else:
            return None

    class Config:
        use_enum_values = False


class MarketUpdateModel(BaseModel):
    symbol: str
    status: BottifyStatus
    notice: Optional[str] = None

    class Config:
        extra = "ignore"
        use_enum_values = True

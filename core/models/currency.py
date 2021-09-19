from pydantic import BaseModel, validator
from core.enums.currency_types import CurrencyType
from core.enums.statuses import BottifyStatus
from typing import Optional, List
from datetime import datetime, timezone
import json


class CurrencyCreateModel(BaseModel):
    name: str
    symbol: str
    currency_type: CurrencyType
    status: BottifyStatus = BottifyStatus.Active  # Should handle restricted trades
    tags: List[str] = []
    token_address: Optional[str] = None


class CurrencyInModel(CurrencyCreateModel):
    currency_type: CurrencyType
    created_at: datetime = datetime.now(tz=timezone.utc)
    tags: str
    token_address: Optional[str] = None

    @validator("status", pre=True)
    def validate_status(cls, v):
        if isinstance(v, BottifyStatus):
            return v.value
        return BottifyStatus.Unset.value

    @validator("tags", pre=True, always=True)
    def dump_tags(cls, v):
        if isinstance(v, list):
            return json.dumps(v)
        return dumps([])


class CurrencyModel(BaseModel):
    id: int = None
    name: str = None
    symbol: str = None
    currency_type: CurrencyType = CurrencyType.Unset
    status: BottifyStatus = BottifyStatus.Unset
    created_at: datetime = None
    tags: List[str] = []
    token_address: Optional[str] = None

    @validator("tags", pre=True, always=True)
    def load_tags(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return []

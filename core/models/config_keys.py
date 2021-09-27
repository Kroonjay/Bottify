from pydantic import BaseModel, validator
from datetime import datetime, timezone
from typing import Optional, TypeVar
from enum import IntEnum
import json

AllowedValueTypes = TypeVar("AllowedValueTypes", int, str, dict, list)


class ConfigKeyCreateModel(BaseModel):
    name: str
    value: AllowedValueTypes
    notes: Optional[str] = None


class ConfigKeyInModel(ConfigKeyCreateModel):
    value: str
    created_at: datetime = datetime.now(tz=timezone.utc)
    modified_at: datetime = datetime.now(tz=timezone.utc)

    @validator("value", pre=True)
    def dump_value(cls, v):
        return json.dumps(v)


class ConfigKeyModel(ConfigKeyCreateModel):
    id: int
    created_at: datetime
    modified_at: datetime

    @validator("value", pre=True)
    def load_value(cls, v):
        return json.loads(v)

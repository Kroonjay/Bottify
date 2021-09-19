from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional


class ConfigKeyCreateModel(BaseModel):
    name: str
    value: str
    notes: Optional[str] = None


class ConfigKeyInModel(ConfigKeyCreate):
    created_at: datetime = datetime.now(tz=timezone.utc)
    modified_at: datetime = datetime.now(tz=timezone.utc)


class ConfigKeyModel(ConfigKeyCreate):
    id: int
    created_at: datetime
    modified_at: datetime

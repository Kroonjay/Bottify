from pydantic import BaseModel, validator
from datetime import datetime, timezone
from typing import List, Dict, Optional
from uuid import uuid4, UUID
import json
import logging

from core.enums.statuses import BottifyStatus
from core.enums.exchanges import Exchange


class StrategyConfigModel(BaseModel):
    tags: List[str] = None


# Used for API Call to Create Strategy, allows for submission of models (not strings) without requirig all attributes that StrategyModel requires
class StrategyCreateModel(BaseModel):
    name: str
    base_currency: str
    config: StrategyConfigModel = StrategyConfigModel()

    @validator("base_currency", pre=True)
    def validate_base_currency_length(cls, v):
        assert len(v) <= 5, f"Base Currency Symbol Must be Less than 5 Characters"
        return v


# Can't inherit Create model because we don't want base_currency string field
class StrategyInModel(BaseModel):
    name: str
    guid: UUID = uuid4()
    user_id: int
    base_currency_id: int
    status: BottifyStatus = BottifyStatus.Active
    created_at: datetime = datetime.now(tz=timezone.utc)
    config: str = None  # Dumped dict containg crypto_id, budget values for any tokens we wish to trade

    @validator("config", pre=True, always=True)
    def dump_config(cls, v):
        if isinstance(v, StrategyConfigModel):
            return v.json()
        elif isinstance(v, dict):
            return StrategyConfigModel(**v).json()
        logging.error(
            f"StrategyInModel:Failed to Dump Config, using Default:Value: {v}"
        )
        return StrategyConfigModel().json()

    class Config:
        extra = "ignore"
        use_enum_values = True


class StrategyModel(BaseModel):
    id: int
    name: str
    guid: UUID
    user_id: int
    base_currency_id: int
    status: BottifyStatus
    created_at: datetime
    config: StrategyConfigModel = None

    @validator("config", pre=True)
    def load_config(cls, v):
        if isinstance(v, StrategyConfigModel):
            return v
        if isinstance(v, str):
            data = json.loads(v)
            if data:
                return StrategyConfigModel(**data)
        if isinstance(v, dict):
            return StrategyConfigModel(**v)
        print(f"ValidationError:StrategyModel:Failed to Load Config:Value: {v}")
        return StrategyConfigModel()

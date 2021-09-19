from pydantic import BaseModel, validator, HttpUrl, ValidationError
from typing import Callable, Dict
from datetime import datetime, timezone
from core.enums.exchanges import Exchange
from core.exchanges.bittrex.api import BittrexApiHelper
from core.enums.statuses import BottifyStatus
from core.exchanges.maps import map_api
import logging
import json


class ExchangeCreateModel(BaseModel):
    name: str
    exchange_type: Exchange
    base_url: HttpUrl
    auth: Dict


class ExchangeInModel(ExchangeCreateModel):
    user_id: int
    auth: str
    status: BottifyStatus = BottifyStatus.Active
    created_at: datetime = datetime.now(tz=timezone.utc)

    @validator("auth", pre=True)
    def dump_auth_dict(cls, v):
        if isinstance(v, dict):
            return json.dumps(v)
        elif isinstance(v, str):
            return v
        return {}

    class Config:
        extra = "ignore"
        use_enum_values = True


class ExchangeModel(BaseModel):
    id: int
    name: str
    user_id: int
    exchange_type: Exchange  # Used to map code paths
    status: BottifyStatus = BottifyStatus.Active
    base_url: HttpUrl
    auth: Dict
    api: Callable = None  # TODO Write a validator to get this based on Exchange Type
    created_at: datetime

    @validator("exchange_type", pre=True, always=True)
    def validate_exchange_type(cls, v):
        if isinstance(v, int):
            return Exchange(v)
        elif isinstance(v, Exchange):
            return v
        else:
            return Exchange.Reserved

    @validator("auth", pre=True, always=True)
    def load_auth(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return {}

    @validator("api", always=True)
    def set_api(cls, v, values):
        api = map_api(values.get("exchange_type"))
        if not api:
            logging.error(
                f"Exchange API Validator : No API For Exchange Type : Exchange Type {values.get('exchange_type')}"
            )
            raise ValidationError("API is Not Yet Supported for this Exchange Type")
        return api


class ExchangeApiModel(BaseModel):
    id: int
    name: str
    exchange_type: Exchange
    status: BottifyStatus
    base_url: HttpUrl
    created_at: datetime

    class Config:
        extra = "ignore"

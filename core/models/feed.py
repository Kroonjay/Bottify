from pydantic import BaseModel, validator
from core.enums.feed_sources import FeedSources
from core.enums.statuses import BottifyStatus
from core.feeds.result_generators import get_feed_result_generator
from core.feeds.result_models import get_feed_result_model
from typing import Type, Callable, Dict, Optional
from datetime import datetime, timedelta, timezone
import uuid
import re

import json


def get_index_name(feed_name: str):
    if isinstance(feed_name, str):
        feed_name_words = re.findall("[A-Z][^A-Z]*", feed_name)
        index_name = "".join([(f"{word.lower()}-") for word in feed_name_words])[
            :-1
        ]  # Strip trailing hyphen off lowercase index name
        return index_name
    return None


class FeedCreateModel(BaseModel):
    feed_name: str
    feed_type: FeedSources
    update_interval: int = 60
    configs: Dict = {}


class FeedInModel(BaseModel):
    feed_type: FeedSources  # FeedTypes enum member
    feed_name: str = None
    index_name: str = None
    update_interval: int = 60  #
    status: BottifyStatus = BottifyStatus.New
    created_at: datetime = None
    last_execution_at: datetime = None
    next_execution_at: datetime = None
    configs: str = None

    @validator("index_name", always=True)
    def set_index_name(cls, v, values, **kwargs):
        assert "feed_name" in values, f"Field Name Required for Index Name"
        return get_index_name(values["feed_name"])

    @validator("created_at", always=True)
    def set_creation_time(cls, v):
        return datetime.now(tz=timezone.utc)

    @validator("last_execution_at", always=True)
    def set_last_execution_time(cls, v):
        if isinstance(v, datetime):
            return v
        else:
            return datetime.now(tz=timezone.utc)

    @validator("next_execution_at", always=True)
    def set_next_execution_time(cls, v, values, **kwargs):
        if isinstance(v, datetime):
            return v
        else:
            if values["update_interval"] and isinstance(
                values["last_execution_at"], datetime
            ):
                update_interval = timedelta(minutes=values["update_interval"])
                return values["last_execution_at"] + update_interval
            else:
                return None

    @validator("configs", pre=True)
    def validate_configs(cls, v):
        if isinstance(v, dict):
            return json.dumps(v)
        return json.dumps({})

    class Config:
        use_enum_values = True


class FeedModel(BaseModel):
    id: int = None
    feed_type: FeedSources = None  # FeedSources enum member
    feed_name: str = None
    index_name: str = None
    update_interval: int = 60  #
    status: BottifyStatus = None
    created_at: datetime = None
    last_execution_at: datetime = None
    next_execution_at: datetime = None
    result_generator: Callable = None
    result_model: BaseModel = None
    configs: Dict = None

    @validator("result_generator", always=True)
    def set_result_generator(cls, v, values, **kwargs):
        assert (
            "feed_type" in values
        ), f"Set Result Generator : Field Type is Missing or Invalid"
        return get_feed_result_generator(values.get("feed_type"))

    @validator("result_model", always=True)
    def set_result_model(cls, v, values, **kwargs):
        assert (
            "feed_type" in values
        ), f"Set Result Model : Feed Type is Missing or Invalid"
        return get_feed_result_model(values.get("feed_type"))

    @validator("configs", pre=True)
    def validate_configs(cls, v):
        if not v:
            return None
        if isinstance(v, str):
            return json.loads(v)
        elif isinstance(v, dict):
            return v
        else:
            print(
                f"Feed Configs Must be a String or Dictionary:Got: {type(v)}:Value: {v}"
            )
            return None


class FeedApiModel(BaseModel):
    id: int = None
    feed_type: FeedSources = None  # FeedSources enum member
    feed_name: str = None
    index_name: str = None
    update_interval: int = None  #
    status: BottifyStatus = None
    created_at: datetime = None
    last_execution_at: datetime = None
    next_execution_at: datetime = None
    configs: Dict = None


class FeedWorkerModel(BaseModel):
    id: int
    feed_type: FeedSources

    class Config:
        use_enum_values = True
        extra = "ignore"
        validate_always = True

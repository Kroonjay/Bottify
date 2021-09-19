from pydantic import BaseModel, validator
from datetime import datetime, timezone, timedelta
from typing import List, Dict
import pytz
import json

from core.enums.statuses import BottifyStatus
from core.enums.alert_type import AlertType
from core.enums.alert_severity import AlertSeverity


class MonitorDefinitionModel(BaseModel):
    name: str


class MonitorCreateModel(BaseModel):
    name: str
    source_id: str
    status: BottifyStatus
    severity: AlertSeverity
    alert_interval: int = 0
    indices: List[str]
    queries: List[Dict]
    definition: Dict
    updated_at: datetime


class MonitorInModel(MonitorCreateModel):
    indices: str
    queries: str
    definition: str
    notes: str = None

    @validator("indices", "queries", "definition", pre=True)
    def dump_values(cls, v):
        if isinstance(v, dict):
            return json.dumps(v)
        elif isinstance(v, list):
            return json.dumps(v)
        else:
            return v

    # @validator("updated_at", pre=True)
    # def add_tz_info(cls, v):
    #     if isinstance(v, datetime):
    #         timezone = pytz.timezone("UTC")
    #         return timezone.localize(v)

    class Config:
        use_enum_values = True


class MonitorModel(MonitorCreateModel):
    id: int
    notes: str = None

    @validator("indices", "queries", "definition", pre=True, always=True)
    def load_values(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        else:
            return v

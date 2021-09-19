from pydantic import BaseModel, validator, ValidationError
from datetime import datetime, timezone
from typing import Dict

import random
import string

from core.enums.statuses import BottifyStatus
from core.enums.indicator_response_actions import IndicatorResponseAction


# Defines an Indicator, used for managing monitors within Elasticsearch, and setting some baseline alert parameters
class IndicatorDefinitionInModel(BaseModel):
    name: str
    monitor_id: str  # Useful for API calls
    status: int = None
    created_at: datetime = None

    monitor_config: str = None
    alert_params: str = None

    @validator("created_at", always=True)
    def set_creation_time(cls, v):
        return datetime.now(tz=timezone.utc)

    @validator("status", always=True)
    def validate_indicator_status(cls, v):
        if isinstance(v, int):
            if v in BottifyStatus.__members__.values():
                return v
        elif isinstance(v, BottifyStatus):
            return v.value
        return BottifyStatus.Active.value

    @validator("alert_params", pre=True)
    def stringify_alert_params(cls, v):
        if isinstance(v, dict):
            return json.dumps(v)
        elif isinstance(v, str):
            return v
        else:
            return None


class IndicatorDefinitionModel(IndicatorDefinitionInModel):
    id: int = None
    es_monitor_name: str = None
    es_trigger_name: str = None
    es_action_name: str = None
    status: BottifyStatus = None

    # @validator("es_monitor_name", always=True)
    # def set_policy_name(cls, values):
    #     assert "name" in values, f"Set Monitor Name Failure:Name is Missing or Invalid"
    #     return f"{values['name']}-Monitor"

    # @validator("es_trigger_name", always=True)
    # def set_trigger_name(cls, values):
    #     assert "name" in values, f"Set Trigger Name Failure:Name is Missing or Invalid"
    #     return f"{values['name']}-Trigger"

    # @validator("es_action_name", always=True)
    # def set_action_name(cls, values):
    #     assert "name" in values, f"Set Action Name Failure:Name is Missing or Invalid"
    #     return f"{values['name']}-Action"

    @validator("status", pre=True)
    def validate_status(cls, v):
        assert (
            v in BottifyStatus.__members__.values()
        ), f"Indicator Status Must be a Member of BottifyStatus:Got: {v}"
        return BottifyStatus(v)


# Incidators are essentially mappings between a given Indicator definition and a strategy that wants to use that indicator.  This allows indicators to be repurposed for multiple strategies, and allows strategies to select a response action for each indicator, rather than having the response_action tied to the indicator def.
class IndicatorInModel(BaseModel):
    strategy_id: int
    definition_id: int
    monitor_id: str
    response_action: int
    status: int = None

    @validator("response_action", always=True)
    def validate_response_action_int(cls, v):
        if isinstance(v, int):
            if v in IndicatorResponseAction.__members__.values():
                return v
        elif isinstance(v, IndicatorResponseAction):
            return v.value
        return IndicatorResponseAction.NoAction.value

    @validator("status", always=True)
    # need to learn how to reuse validators
    def validate_iim_status(cls, v):
        if isinstance(v, int):
            if v in BottifyStatus.__members__.values():
                return v
        elif isinstance(v, BottifyStatus):
            return v.value
        return BottifyStatus.Active.value


class IndicatorModel(IndicatorInModel):
    id: int = None
    response_action: IndicatorResponseAction = None
    status: BottifyStatus = None

    @validator("response_action", pre=True)
    def load_response_action(cls, v):
        if isinstance(v, int):
            if v in IndicatorResponseAction.__members__.values():
                return IndicatorResponseAction(v)
        elif isinstance(v, IndicatorResponseAction):
            return v
        print(
            f"IndicatorModel ValidationError:Failed to Set Response Action:Value: {v}"
        )
        return None

    @validator("status", pre=True)
    def load_status(cls, v):
        if isinstance(v, int):
            if v in BottifyStatus.__members__.values():
                return BottifyStatus(v)
        elif isinstance(v, BottifyStatus):
            return v
        print(f"IndicatorModel ValidationError:Failed to Set Status:Value: {v}")
        return None

from pydantic import BaseModel, validator, ValidationError, conint
from typing import List, Optional
from datetime import datetime, timezone
from core.enums.orders import OrderDirection, OrderType, OrderTimeInForce
from core.enums.statuses import BottifyStatus
from core.enums.alert_type import AlertType


class ReactionCreateModel(BaseModel):
    monitor_id: int
    direction: OrderDirection
    amount: conint(gt=0, lt=100)  # Percentage of available budget to spend
    time_in_force: OrderTimeInForce = OrderTimeInForce.GoodTilCancelled


class ReactionInModel(ReactionCreateModel):
    created_at: datetime = datetime.now(tz=timezone.utc)
    status: BottifyStatus = BottifyStatus.Active

    class Config:
        use_enum_values = True


class ReactionModel(ReactionCreateModel):
    id: int
    created_at: datetime
    status: BottifyStatus

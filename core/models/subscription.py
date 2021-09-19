from pydantic import BaseModel
from datetime import datetime, timezone


class SubscriptionInModel(BaseModel):
    monitor_id: int
    strategy_id: int
    reaction_id: int
    created_at: datetime = datetime.now(tz=timezone.utc)


class SubscriptionModel(SubscriptionInModel):
    id: int
    created_at: datetime

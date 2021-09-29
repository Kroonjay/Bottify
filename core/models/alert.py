from pydantic import BaseModel, validator, condecimal
from datetime import datetime, timezone
from typing import List, Optional
import json
import logging
from core.config import settings
from core.enums.exchanges import Exchange
from core.enums.statuses import BottifyStatus
from core.enums.alert_type import AlertType

# Alerts are created whenever an ElasticSearch monitor fires and forwards data to our webhook.  Webhook creates a task to lookup all strategies using this monitor_id and trigger their appropriate response_actions
class AlertCreateModel(BaseModel):
    source_id: str
    trigger_id: str
    severity: int
    period_start: datetime
    period_end: datetime
    total_results: int
    exchange: Optional[Exchange] = None
    currency: Optional[str] = None  # List of Currency Slugs "BTC", "USD"
    market: Optional[str] = None  # List of Market Slugs "BTC-USD", "BTC-XRP"
    price: Optional[
        condecimal(
            ge=0,
            lt=100000000,  # Maximum balance must be under 100 Million (8 digits) in order to maintain 8 decimal places
            max_digits=settings.BalanceMaximumDigits,
            decimal_places=settings.BalanceDecimalPrecision,
        )
    ] = None


class AlertInModel(AlertCreateModel):
    monitor_id: int
    status: BottifyStatus = BottifyStatus.Active
    created_at: datetime = datetime.now(tz=timezone.utc)

    class Config:
        use_enum_values = True
        max_anystr_length = 120


class AlertModel(AlertCreateModel):
    id: int
    status: BottifyStatus
    created_at: datetime

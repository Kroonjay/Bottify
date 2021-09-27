from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime
from core.enums.candle_length import CandleLength


class CandleModel(BaseModel):
    exchange_id: int
    market_symbol: str
    length: CandleLength
    low: Decimal
    high: Decimal
    open: Decimal
    close: Decimal
    volume: Decimal
    time: datetime

    class Config:
        use_enum_values = True

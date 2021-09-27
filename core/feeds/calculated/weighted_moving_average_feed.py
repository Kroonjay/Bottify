from core.elasticsearch.api import ElasticApiHelper
from core.database.crud.market import read_markets_by_tags
from pydantic import BaseModel
from datetime import dateteime, timezone, timedelta
import pandas as pd
import numpy as np
from pandas.io.json import json_normalize


class WeightedMovingAverageModel(BaseModel):
    market_symbol: str
    date: datetime


# TODO Finish this after we add support for candles
def weighted_moving_average_result_generator(configs: dict):
    pass

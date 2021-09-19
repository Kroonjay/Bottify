import sqlalchemy as sa
from asyncpg.exceptions import (
    UniqueViolationError,
    ForeignKeyViolationError,
    NotNullViolationError,
)
from pydantic import BaseModel, ValidationError
from databases import Database

from core.configs.db_config import MAIN_DB_CONN_STRING
from core.database.tables.feeds import get_feeds_table
from core.database.tables.alert import get_alert_table
from core.database.tables.bottify_user import get_bottify_user_table
from core.database.tables.indicator import get_indicator_table
from core.database.tables.indicator_definition import get_indicator_definition_table
from core.database.tables.strategy import get_strategy_table
from core.database.tables.currency import get_currency_table
from core.database.tables.exchange import get_exchange_table
from core.database.tables.balance import get_balance_table
from core.database.tables.market import get_market_table
from core.database.tables.bottify_order import get_bottify_order_table
from core.database.tables.trade import get_trade_table
from core.database.tables.budget import get_budget_table
from core.database.tables.subscription import get_subscription_table
from core.database.tables.monitor import get_monitor_table
from core.database.tables.reaction import get_reaction_table
from core.database.tables.config_key import get_config_key_table
from core.database.database import get_db

import logging


def create_tables():
    engine = sa.create_engine(MAIN_DB_CONN_STRING)
    meta = sa.MetaData()
    get_bottify_user_table(meta)
    get_feeds_table(meta)
    get_alert_table(meta)
    get_indicator_table(meta)  # Deprecated
    get_indicator_definition_table(meta)  # Deprecated
    get_strategy_table(meta)
    get_currency_table(meta)
    get_exchange_table(meta)
    get_balance_table(meta)
    get_market_table(meta)
    get_bottify_order_table(meta)
    get_trade_table(meta)
    get_budget_table(meta)
    get_subscription_table(meta)
    get_monitor_table(meta)
    get_reaction_table(meta)
    get_config_key_table(meta)
    meta.create_all(engine)


# Helper function to build models from database rows, handles ValidationErrors
def build_model_from_row(row_data: dict, model: BaseModel):
    if not row_data:
        logging.debug(f"Build Model from Row Data : Row Data is None")
        return None
    try:
        return model(**row_data)
    except ValidationError as ve:
        logging.warning(
            f"Failed to Build Model from Row : {type(model)} : ValidationError : {ve.json()}"
        )
        return None


async def write_db(database: Database, query: str, values: dict = None):
    if not isinstance(values, dict):
        logging.error(
            f"Write DB - Invalid Input - Required: Dict - Got: {type(values)}"
        )
        return False
    try:
        if values:
            result = await database.execute(query, values=values)
        else:
            result = await database.execute(query)
        logging.debug(f"Write DB - Success - Model: {type(values)}")
        return True
    except UniqueViolationError as uve:
        logging.error(f"Write DB : Unique Key Violation : {uve}")
    except ForeignKeyViolationError as fkve:
        logging.error(f"Write DB : Foreign Key Violation : {fkve}")
    except NotNullViolationError as nnve:
        logging.error(f"Write DB : Not-Null Violation : {nnve}")
    return False

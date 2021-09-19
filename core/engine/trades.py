import logging
from pydantic import ValidationError


from core.database.database import get_db
from core.models.trade import TradeInModel
from core.database.crud.market import read_market_by_id
from core.database.crud.exchange import read_exchange_by_id
from core.database.crud.bottify_order import create_order
from core.models.order import BottifyOrderCreateModel, BottifyOrderInModel
from core.database.crud.trade import read_trade_by_id, read_trade_by_source_id

# 99.99999% sure this is garbage
async def async_work_place_trade(order_create: BottifyOrderCreateModel):
    async with get_db() as database:
        if not isinstance(order_create, BottifyOrderCreateModel):
            logging.error(
                f"Async Work Place Trade : Input Must be BottifyOrderCreateModel : Got {type(order_create)}"
            )
            return False
        market = await read_market_by_id(database, order_create.market_id)
        if not market:
            logging.error(
                f"Async Work Place Trade : Market is None : Market ID: {str(market_id)}"
            )
            return False
        exchange = await read_exchange_by_id(database, market.exchange_id)
        if not exchange:
            logging.error(
                f"Async Work Place Trade : Exchange is None : Exchange ID {market.exchange_id}"
            )
            return False
        # TODO Need to build in actual trade support on exchanges first...
        try:
            order_in = BottifyOrderInModel(**order_create.dict())
        except ValidationError as ve:
            logging.error(f"Async Work Place Trade : ValidationError : {ve.json()}")
            return False
        success = await create_order(database, order_in)

    return True

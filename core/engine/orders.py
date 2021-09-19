import logging
from pydantic import ValidationError
from databases import Database
from core.enums.budget_results import BudgetResult
from core.models.budget import BudgetInModel
from core.enums.orders import OrderDirection
from core.enums.statuses import BottifyStatus
from core.models.exchange import ExchangeModel
from core.models.market import MarketModel
from core.database.database import create_db
from core.models.order import BottifyOrderCreateModel, BottifyOrderModel
from core.database.crud.market import read_market_by_id
from core.database.crud.trade import (
    create_trade,
    read_trade_by_source_id,
    read_trade_by_id,
)
from core.models.budget import BudgetModel
from core.database.crud.exchange import read_exchange_by_id
from core.database.crud.bottify_order import (
    create_order,
    read_open_orders,
    update_order_status,
    read_order_by_id,
)
from core.database.crud.budget import (
    read_budget_by_currency_exchange_strategy,
    lock_budget,
    debit_budget,
    credit_budget,
    create_budget,
)


async def async_work_place_order(order_in: BottifyOrderCreateModel):
    if not isinstance(order_in, BottifyOrderCreateModel):
        logging.error(
            f"Place Order : Input Must be a BottifyOrderCreateModel : Got {type(order_in)}"
        )
        return
    async with create_db() as database:
        market = await read_market_by_id(database, order_in.market_id)
        if not market:
            logging.error(
                f"Place Order : No Market Found for ID : Market ID {order_in.market_id}"
            )
            return
        exchange = await read_exchange_by_id(database, market.exchange_id)
        if not exchange:
            logging.error(
                f"Place Order : No Exchange Found for Market : Exchange ID {market.exchange_id}"
            )
            return
        budget = None
        if (
            order_in.direction == OrderDirection.Buy
        ):  # We're spending our quote currency to get more base currency
            budget = await read_budget_by_currency_exchange_strategy(
                database, market.quote_currency_id, exchange.id, order_in.strategy_id
            )
        elif (
            order_in.direction == OrderDirection.Sell
        ):  # We're spending our base currency to get more quote currency
            budget = await read_budget_by_currency_exchange_strategy(
                database, market.base_currency_id, exchange.id, order_in.strategy_id
            )
        if not budget:
            logging.error(f"Place Order : No Budget : Direction {order_in.direction}")
            return
        response = await lock_budget(
            database, budget.id, order_in.quantity
        )  # Lock Budget, will remain locked until order is cancelled (unlocked) or spent on other currencies (credit)
        if not response == BudgetResult.Success:
            logging.error(
                f"Place Order : Failed to Lock Budget : {str(response)} : Order Details {order_in.json()}"
            )
            return
        new_bottify_order = exchange.api(exchange).place_order(order_in, market.symbol)
        created = await create_order(database, new_bottify_order)
        if not created:
            logging.error(f"Work Place Order : Failed to Create Order in Database")
            return


async def async_work_refresh_open_orders():
    order_counter = 0
    db = create_db()
    async with db as database:
        open_orders = await read_open_orders(database)
        if not open_orders:
            logging.error("Work Refresh Open Orders : No Open Orders")
            return
        num_orders = len(open_orders)
        for order in open_orders:
            order_counter += 1
            market = await read_market_by_id(database, order.market_id)
            if not market:
                logging.error(
                    f"Work Refresh Open Orders : No Market Found for Order : Order ID {order.id} : Market ID {order.market_id}"
                )
                continue
            exchange = await read_exchange_by_id(database, market.exchange_id)
            if not exchange:
                logging.error(
                    f"Work Refresh Open Orders : No Exchange Found for Order Market : Market ID {market.id} : Exchange ID {market.exchange_id}"
                )
                continue
            exchange_order = exchange.api(exchange).get_order(order)
            if not exchange_order:
                logging.error(
                    "Work Refresh Open Orders : Failed to Retrieve Updated Order from Exchange"
                )
                continue

            trades_handled = await handle_trades(database, order, exchange, market)
            if trades_handled and exchange_order.status == BottifyStatus.Complete:
                success = await update_order_status(
                    database, order.id, exchange_order.status
                )
                if not success:
                    logging.error(
                        f"Work Refresh Open Orders : Failed to Update Order Status in Database : Order ID {order.id} : New Status {updated_order.status}"
                    )

            logging.info(
                f"Work Refresh Open Orders : {order_counter} of {num_orders} Complete : Success True"
            )


async def handle_budget(
    database: Database, currency_id: int, exchange_id: int, strategy_id: int
):
    budget = await read_budget_by_currency_exchange_strategy(
        database, currency_id, exchange_id, strategy_id
    )
    if budget:
        return budget

    logging.info("Handle Budget : Creating New Budget")
    try:
        new_budget = BudgetInModel(
            currency_id=currency_id,
            exchange_id=exchange_id,
            strategy_id=strategy_id,
        )
    except ValidationError as ve:
        logging.error(f"Handle Budget : BudgetInModel : ValidationError : {ve.json()}")
    await create_budget(database, new_budget)
    return await read_budget_by_currency_exchange_strategy(
        database, currency_id, exchange_id, strategy_id
    )


async def handle_trades(
    database: Database,
    order: BottifyOrderModel,
    exchange: ExchangeModel,
    market: MarketModel,
):
    trades = exchange.api(exchange).get_trades_by_order(order.source_id, order.id)
    if not trades:
        logging.error("Handle Trades : Failed to Retrieve Order Trades from Exchange")
        return False
    num_trades = len(trades)
    trade_counter = 0
    for trade in trades:
        trade_counter += 1
        db_trade = await read_trade_by_source_id(database, trade.source_id)
        if db_trade:
            logging.info("Handle Trades : Trade Already Exists in DB : Skipping")
            continue

        if (
            order.direction == OrderDirection.Buy
        ):  # We spent our quote currency to get more base currency
            debit_currency = market.base_currency_id
            credit_currency = market.quote_currency_id
        elif (
            order.direction == OrderDirection.Sell
        ):  # We spent our base currency to get more quote currency
            debit_currency = market.quote_currency_id
            credit_currency = market.base_currency_id
        else:
            logging.info(
                f"Handle Trades : Trade has Invalid Order Direction : Skipping : Order Direction {order.direction}"
            )
            continue
        budget_to_credit = await handle_budget(
            database, credit_currency, exchange.id, order.strategy_id
        )
        if not budget_to_credit:
            logging.error("Handle Trades : Error Handling Credit Budget : Skipping")
            continue
        budget_to_debit = await handle_budget(
            database, debit_currency, exchange.id, order.strategy_id
        )
        if not budget_to_debit:
            logging.error(f"Handle Trades : Error Handling Debit Budget : Skipping")
            continue
        # Credit Budget, subtract price from credit currencies reserved balance
        credit_success = await credit_budget(database, budget_to_credit.id, trade.price)
        if not credit_success:
            logging.error("Handle Trades : Failed to Credit Budget : Skipping")
            continue
        # Debit Budget, add trade quantity to debit currencies available balance
        debit_success = await debit_budget(database, budget_to_debit.id, trade.quantity)
        if not debit_success:
            logging.critical(
                f"Handle Trades : Failed to Debit Budget, Budget Already Credited : Debit Budget ID {budget_to_debit.id} : Credit Budget ID {budget_to_credit.id}"
            )
            continue
        await create_trade(database, trade)
        logging.info(
            f"Handle Trades : {trade_counter} of {num_trades} Complete : Success True"
        )
    return True

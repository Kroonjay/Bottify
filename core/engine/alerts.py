import logging
from pydantic import ValidationError
from databases import Database
from decimal import Decimal
from core.database.database import create_db
from core.database.crud.alert import read_alert_by_id
from core.database.crud.subscription import read_subscriptions_by_monitor_id
from core.database.crud.strategy import read_strategy_by_id
from core.database.crud.exchange import (
    read_active_exchanges_by_user,
    read_active_exchange_by_user_exchange_type,
)
from core.database.crud.market import (
    read_market_by_exchange_symbol,
    read_market_by_base_quote_exchange_ids,
)
from core.database.crud.reaction import read_reaction_by_id
from core.database.crud.currency import read_currency_by_symbol, read_currency_by_id
from core.database.crud.budget import read_budget_by_currency_exchange_strategy
from core.engine.orders import async_work_place_order
from core.enums.statuses import BottifyStatus
from core.models.alert import AlertModel, AlertInModel
from core.models.reaction import ReactionModel
from core.models.monitor import MonitorModel
from core.models.order import BottifyOrderCreateModel
from core.models.strategy import StrategyModel
from core.enums.orders import OrderDirection, OrderTimeInForce, OrderType
from core.enums.alert_type import AlertType


# ASKTAN
async def async_work_handle_reaction(
    reaction_id: int, strategy_id: int, alert: AlertInModel
):

    if not isinstance(alert, AlertInModel):
        logging.error(
            f"Handle Reaction : Alert Must be AlertInModel : Got {type(alert)}"
        )
        return
    exchanges = []
    markets = []
    async with create_db() as database:
        reaction = await read_reaction_by_id(database, reaction_id)
        if not reaction:
            logging.error(
                f"Handle Reaction : No Reaction For ID : ID {str(reaction_id)}"
            )
            return

        strategy = await read_strategy_by_id(database, strategy_id)
        if not strategy:
            logging.error(
                f"Handle Reaction : No Strategy for ID : ID {str(strategy_id)}"
            )
            return
        base_currency = await read_currency_by_id(database, strategy.base_currency_id)
        if not base_currency:
            logging.error(
                f"Handle Reaction : Invalid Base Currency ID for Strategy : ID {strategy.base_currency_id}"
            )
            return
        if alert.price:
            order_type = OrderType.Limit
        else:
            order_type = OrderType.Market
        if alert.exchange:
            exchange = await read_active_exchange_by_user_exchange_type(
                database, strategy.user_id, alert.exchange
            )
            if not exchange:
                logging.error(
                    f"Handle Reaction : Alert Exchange Param is Invalid : Requires Exchange : Got {alert.exchange}"
                )
                return
            else:
                exchanges.append(exchange)
        else:
            exchanges.extend(
                await read_active_exchanges_by_user(database, strategy.user_id)
            )
        for exchange in exchanges:
            direction = reaction.direction
            market = None
            if alert.market:
                market = await read_market_by_exchange_symbol(
                    database, exchange.id, alert.market
                )
                if not market:
                    logging.error(
                        f"Handle Reaction : No Exchange Market Found for Alert Market : Market Symbol {str(alert.market)} : Exchange ID {exchange.id}"
                    )
                    continue
                else:
                    markets.append(alert_market)
            elif alert.currency:
                alert_currency = await read_currency_by_symbol(database, alert.currency)
                if not alert_currency:
                    logging.error(
                        f"Handle Reaction : Alert Currency Param is Invalid : Requires CurrencySymbol String : Got {str(alert.currency)}"
                    )
                    return
                if alert_currency.id == strategy.base_currency_id:
                    logging.error(
                        f"Handle Reaction : Alert Currency is Equal to Strategy Base Currency : Alert Currency {alert_currency.symbol} : Base Currency {strategy.base_currency_id}"
                    )
                    return
                market = await read_market_by_base_quote_exchange_ids(
                    database, alert_currency.id, base_currency.id, exchange.id
                )
                if not market:
                    logging.warning(
                        f"Handle Reaction : No Exchange Market Found for Alert Currency : Base Currency {base_currency.symbol} : Alert Currency {alert_currency.symbol} : Exchange {exchange.name}"
                    )
                    continue
                else:
                    markets.append(market)
            else:
                logging.error(
                    f"Handle Reaction : Either Market or Currency is Required, Found Neither"
                )
                return
            budget = None
            if reaction.direction == OrderDirection.Buy:
                # We're spending our base currency
                budget = await read_budget_by_currency_exchange_strategy(
                    database, base_currency.id, market.exchange_id, strategy.id
                )  # TODO Pretty sure we have a problem if we need to sell ETH (it is never a quote currency for any exchange markets)
            elif reaction.direction == OrderDirection.Sell:
                # We need to spend the quote curreny
                budget = await read_budget_by_currency_exchange_strategy(
                    database, alert_currency.id, market.exchange_id, strategy.id
                )
            else:
                logging.error(
                    f"Handle Reaction : Unsupported Order Direction : {str(reaction.direction)}"
                )
                return
            if not budget:
                logging.error(
                    f"Handle Reaction : No Budget Found for Market : Direction {reaction.direction} : Market {market.symbol} : Exchange {market.exchange_id} : Strategy {strategy.id}"
                )
                continue

            try:
                new_order = BottifyOrderCreateModel(
                    strategy_id=strategy.id,
                    market_id=market.id,
                    direction=reaction.direction,
                    order_type=order_type,
                    time_in_force=reaction.time_in_force,
                )
                if alert.price:
                    order_price = alert.price
                    new_order.price = (
                        alert.price
                    )  # Set New Order's Price for limit orders
                else:
                    ticker = exchange.api(exchange).get_ticker(market.symbol)
                    if not ticker:
                        logging.error(
                            f"Handle Reaction : Get Ticker Failed to Retrieve Market Price"
                        )
                        continue
                    order_price = (
                        ticker.price
                    )  # Don't assign New Order's Price for Market orders, but get the unit price for use in quantity calculation
                new_order.quantity = budget.available * Decimal((reaction.amount / 100))
            except ValidationError as ve:
                logging.error(
                    f"Handle Reaction : BottifyOrderCreateModel : ValidationError : {ve.json()}"
                )
                continue
            await async_work_place_order(new_order)

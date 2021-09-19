import logging
from pydantic import ValidationError


from core.database.database import create_db
from core.database.crud.exchange import (
    read_exchange_by_id,
    read_active_exchanges_by_user,
)
from core.database.crud.balance import (
    read_balance_by_currency_exchange,
    update_balance,
    create_balance,
)
from core.database.crud.currency import read_currency_by_symbol
from core.exchanges.helpers import transform_exchange_balance
from core.models.balance import CurrencyBalanceInModel


async def async_work_update_exchange_balances(exchange_id: int):
    async with create_db() as database:
        exchange = await read_exchange_by_id(database, exchange_id)
        if not exchange:
            logging.error(
                f"Update Exchange Balances : Exchange is None : Exchange ID {str(exchange_id)}"
            )
            return False
        exchange_balances = exchange.api(exchange).get_balances()
        for exchange_balance in exchange_balances:
            currency = await read_currency_by_symbol(
                database,
                exchange_balance.symbol,  # This assumes all possible exchange_balance objects use an alias to ensure symbol is a common field
            )
            if not currency:
                logging.error(
                    f"Update Exchange Balances : No Currency Row for Symbol : Symbol {str(exchange_balance.symbol)} "
                )
                continue
            new_balance = transform_exchange_balance(
                exchange_balance, exchange.id, exchange.exchange_type, currency.id
            )
            if not new_balance:
                logging.error(f"Update Exchange Balances : Failed to Transform Balance")
                continue
            db_balance = await read_balance_by_currency_exchange(
                database,
                currency.id,
                exchange.id,
            )
            if not db_balance:
                logging.info(
                    f"Update Exchange Balances : No Balance Row for Exchange Balance : Creating"
                )
                success = await create_balance(database, new_balance)
                if not success:
                    logging.error(
                        f"Update Exchange Balances : Failed to Create New Balance"
                    )
            else:
                await update_balance(database, db_balance.id, new_balance)


async def async_work_update_user_balances(user_id: int):
    async with create_db() as database:
        exchanges = await read_active_exchanges_by_user(database, user_id)
        for exchange in exchanges:
            await async_work_update_exchange_balances(exchange.id)

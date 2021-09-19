import logging

from databases import Database
from decimal import Decimal
from sqlalchemy import and_
from core.database.helpers import build_model_from_row, write_db
from core.database.tables.balance import get_balance_table
from core.models.balance import CurrencyBalanceInModel, CurrencyBalanceModel

balance_table = get_balance_table()


async def create_balance(database: Database, balance_in: CurrencyBalanceInModel):
    if not isinstance(balance_in, CurrencyBalanceInModel):
        logging.error(
            f"Create Balance : Input Must be CurrencyBalanceInModel : Got {type(balance_in)}"
        )
        return False
    query = balance_table.insert()
    return await write_db(database, query, balance_in.dict())


async def read_all_balances(database: Database, limit: int):
    balances = []
    if not isinstance(limit, int):
        logging.error(
            f"Read All Balances : Limit Must be an Integer : Got {type(limit)}"
        )
        return balances
    query = balance_table.select().limit(limit)
    async for row in database.iterate(query):
        balances.append(build_model_from_row(row, CurrencyBalanceModel))
    if not balances:
        logging.error(f"Read All Balances : No Results")
    return balances


async def read_balance_by_id(database: Database, balance_id: int):
    if not isinstance(balance_id, int):
        logging.error(
            f"Read Balance by ID : Balance ID Must be an Integer : Got {type(balance_id)}"
        )
        return None
    query = balance_table.select().where(balance_table.c.id == balance_id).limit(1)
    row = await database.fetch_one(query)
    return build_model_from_row(row, CurrencyBalanceModel)


async def read_balance_by_currency_exchange(
    database: Database, currency_id: int, exchange_id: int
):
    query = (
        balance_table.select()
        .where(
            and_(
                balance_table.c.currency_id == currency_id,
                balance_table.c.exchange_id == exchange_id,
            )
        )
        .limit(1)
    )
    row = await database.fetch_one(query)
    return build_model_from_row(row, CurrencyBalanceModel)


async def read_user_balances(database: Database, user_id: int):
    balances = []
    if not isinstance(user_id, int):
        logging.error(
            f"Read User Balances : User ID Must be an Integer : Got {type(user_id)}"
        )
        return balances
    query = balance_table.select().where(balance_table.c.user_id == user_id)
    async for row in database.iterate(query):
        balances.append(build_model_from_row(row, CurrencyBalanceModel))
    if not balances:
        logging.error(f"Read User Balances : No Results")
    return balances


async def read_exchange_balances(database: Database, exchange_id: int):
    balances = []
    if not isinstance(strategy_id, int):
        logging.error(
            f"Read Exchange Balances : Exchange ID Must be an Integer : Got {type(exchange_id)}"
        )
        return balances
    query = balance_table.select().where(balance_table.c.exchange_id == exchange_id)
    async for row in database.iterate(query):
        balances.append(build_model_from_row(row, CurrencyBalanceModel))
    if not balances:
        logging.error(f"Read Exchange Balances : No Results")
    return balances


async def debit_available(database: Database, balance_id: int, amount: Decimal) -> bool:
    success = False
    if not isinstance(balance_id, int):
        logging.error(
            f"Update Balance Debit : Balance ID Must be an Integer : Got {type(balance_id)}"
        )
        return success
    if not isinstance(debit_amount, Decimal):
        logging.error(
            f"Update Balance Debit : Debit Amount Must be a Decimal : Got {type(debit_amount)}"
        )
        return success
    query = "Call BalanceDebitAvailable(:balance_id, :amount)"
    result = await database.execute(
        query, values={"balance_id": balance_id, "amount": amount}
    )
    return True


async def update_balance(
    database: Database, balance_id: int, balance_in: CurrencyBalanceInModel
):
    if not isinstance(balance_in, CurrencyBalanceInModel):
        logging.error(
            f"Update Balance : Input Must be a CurrencyBalanceInModel : Got {type(balance_in)}"
        )
        return False
    query = (
        balance_table.update()
        .where(balance_table.c.id == balance_id)
        .values(
            {
                "available": balance_in.available,
                "reserved": balance_in.reserved,
                "updated_at": balance_in.updated_at,
            }
        )
    )
    await database.execute(query)
    return True

import logging
from asyncpg.exceptions import RaiseError
from databases import Database
from decimal import Decimal
from sqlalchemy import and_
from core.database.helpers import build_model_from_row, write_db
from core.database.tables.budget import get_budget_table
from core.models.budget import BudgetInModel, BudgetModel
from core.enums.budget_results import BudgetResult

budget_table = get_budget_table()


async def create_budget(database: Database, budget_in: BudgetInModel):
    if not isinstance(budget_in, BudgetInModel):
        logging.error(
            f"Create Budget : Input Must be BudgetInModel : Got {type(budget_in)}"
        )
        return False
    query = budget_table.insert()
    return await write_db(database, query, budget_in.dict())


async def read_all_budgets(database: Database, limit: int):
    budgets = []
    if not isinstance(limit, int):
        logging.error(
            f"Read All Budgets : Limit Must be an Integer : Got {type(limit)}"
        )
        return budgets
    query = budget_table.select().limit(limit)
    async for row in database.iterate(query):
        budgets.append(build_model_from_row(row, BudgetModel))
    if not budgets:
        logging.error(f"Read All Budgets : No Results")
    return budgets


async def read_budget_by_id(database: Database, budget_id: int):
    if not isinstance(budget_id, int):
        logging.error(
            f"Read Budget by ID : Budget ID Must be an Integer : Got {type(budget_id)}"
        )
        return None
    query = budget_table.select().where(budget_table.c.id == budget_id).limit(1)
    row = await database.fetch_one(query)
    return build_model_from_row(row, BudgetModel)


async def read_budget_by_currency_exchange_strategy(
    database: Database, currency_id: int, exchange_id: int, strategy_id: int
):
    query = (
        budget_table.select()
        .where(
            and_(
                budget_table.c.currency_id == currency_id,
                budget_table.c.exchange_id == exchange_id,
                budget_table.c.strategy_id == strategy_id,
            )
        )
        .limit(1)
    )
    row = await database.fetch_one(query)
    return build_model_from_row(row, BudgetModel)


async def read_strategy_budgets(database: Database, strategy_id: int):
    budgets = []
    if not isinstance(strategy_id, int):
        logging.error(
            f"Read Strategy Budgets : Strategy ID Must be an Integer : Got {type(strategy_id)}"
        )
        return budgets
    query = budget_table.select().where(budget_table.c.strategy_id == strategy_id)
    async for row in database.iterate(query):
        budgets.append(build_model_from_row(row, BudgetModel))
    if not budgets:
        logging.error(f"Read User Budgets : No Results")
    return budgets


async def read_exchange_budgets(database: Database, exchange_id: int):
    budgets = []
    if not isinstance(strategy_id, int):
        logging.error(
            f"Read Exchange Budgets : Exchange ID Must be an Integer : Got {type(exchange_id)}"
        )
        return budgets
    query = budget_table.select().where(budget_table.c.exchange_id == exchange_id)
    async for row in database.iterate(query):
        budgets.append(build_model_from_row(row, BudgetModel))
    if not budgets:
        logging.error(f"Read Exchange Budgets : No Results")
    return budgets


async def update_budget(database: Database, budget_id: int, budget_in: BudgetInModel):
    if not isinstance(budget_in, BudgetInModel):
        logging.error(
            f"Update Budget : Input Must be a BudgetInModel : Got {type(budget_in)}"
        )
        return False
    query = (
        budget_table.update()
        .where(budget_table.c.id == budget_id)
        .values(
            {
                "available": budget_in.available,
                "reserved": budget_in.reserved,
                "updated_at": budget_in.updated_at,
            }
        )
    )
    await database.execute(query)
    return True


def map_budget_error(re: RaiseError):
    for result in BudgetResult:
        if result.name in str(re):
            return result
    logging.error(f"Map Budget Error : Unknown Result : {str(re)}")
    return BudgetResult.Unset


async def lock_budget(database: Database, budget_id: int, amount: Decimal):
    if not isinstance(budget_id, int):
        logging.error(
            f"Lock Budget : Budget ID Must be an Integer : Got {type(budget_id)}"
        )
        return BudgetResult.InvalidFunctionParameter
    if not isinstance(amount, Decimal):
        logging.error(f"Lock Budget : Amount Must be a Decimal : Got {type(amount)}")
        return BudgetResult.InvalidFunctionParameter
    query = "Call BudgetLock(:budget_id, :amount);"
    values = {"budget_id": budget_id, "amount": amount}
    try:
        await database.execute(query, values=values)
        return BudgetResult.Success
    except RaiseError as re:
        return map_budget_error(re)


async def unlock_budget(database: Database, budget_id: int, amount: Decimal):
    if not isinstance(budget_id, int):
        logging.error(
            f"Unlock Budget : Budget ID Must be an Integer : Got {type(budget_id)}"
        )
        return BudgetResult.InvalidFunctionParameter
    if not isinstance(amount, Decimal):
        logging.error(f"Unlock Budget : Amount Must be a Decimal : Got {type(amount)}")
        return BudgetResult.InvalidFunctionParameter
    query = "Call BudgetUnlock(:budget_id, :amount);"
    values = {"budget_id": budget_id, "amount": amount}
    try:
        await database.execute(query, values=values)
        return BudgetResult.Success
    except RaiseError as re:
        return map_budget_error(re)


async def debit_budget(database: Database, budget_id: int, amount: Decimal):
    if not isinstance(budget_id, int):
        logging.error(
            f"Debit Budget : Budget ID Must be an Integer : Got {type(budget_id)}"
        )
        return BudgetResult.InvalidFunctionParameter
    if not isinstance(amount, Decimal):
        logging.error(f"Debit Budget : Amount Must be a Decimal : Got {type(amount)}")
        return BudgetResult.InvalidFunctionParameter
    query = "Call BudgetDebit(:budget_id, :amount);"
    values = {"budget_id": budget_id, "amount": amount}
    try:
        await database.execute(query, values=values)
        return BudgetResult.Success
    except RaiseError as re:
        return map_budget_error(re)


async def credit_budget(database: Database, budget_id: int, amount: Decimal):
    if not isinstance(budget_id, int):
        logging.error(
            f"Credit Budget : Budget ID Must be an Integer : Got {type(budget_id)}"
        )
        return BudgetResult.InvalidFunctionParameter
    if not isinstance(amount, Decimal):
        logging.error(f"Credit Budget : Amount Must be a Decimal : Got {type(amount)}")
        return BudgetResult.InvalidFunctionParameter
    query = "Call BudgetCredit(:budget_id, :amount);"
    values = {"budget_id": budget_id, "amount": amount}
    try:
        await database.execute(query, values=values)
        return BudgetResult.Success
    except RaiseError as re:
        return map_budget_error(re)

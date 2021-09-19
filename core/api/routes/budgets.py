import logging
from pydantic import ValidationError
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from databases import Database
from typing import Optional, List

from core.models.user import BottifyUserModel
from core.security.login_helpers import authenticate_user, user_is_god
from core.database.database import get_db
from core.models.budget import BudgetInModel, BudgetModel
from core.database.crud.budget import (
    read_all_budgets,
    read_budget_by_id,
    create_budget,
    read_strategy_budgets,
)
from core.database.crud.strategy import read_user_strategies


router = APIRouter()


@router.post("/budget/create")
async def post_budget(
    budget_in: BudgetInModel,
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
):
    success = await create_budget(database, budget_in)
    result = False
    if success:
        result = True
    return JSONResponse(content={"success": result})


@router.get("/budgets", response_model=List[BudgetModel])
async def get_budgets(
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
    limit: Optional[int] = 100,
):
    budgets = []
    if user_is_god(user):
        budgets.extend(await read_all_budgets(database, limit))
    else:
        for strategy in await read_user_strategies(database, user.id):
            budgets.extend(await read_strategy_budgets(database, strategy.id))
    return budgets


@router.get("/budget/{budget_id}", response_model=BudgetModel)
async def get_budget(
    budget_id: int,
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
):
    return await read_budget_by_id(database, budget_id)

import logging
from pydantic import ValidationError
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from databases import Database
from typing import Optional, List
from core.worker import bottify_worker
from core.models.user import BottifyUserModel
from core.security.login_helpers import authenticate_user
from core.database.database import get_db
from core.models.balance import CurrencyBalanceInModel, CurrencyBalanceModel
from core.database.crud.balance import (
    create_balance,
    read_all_balances,
    read_balance_by_id,
)


router = APIRouter()


@router.get("/balance/{balance_id}", response_model=CurrencyBalanceModel)
async def get_balance(
    balance_id: int,
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
):
    return await read_balance_by_id(database, balance_id)


@router.get("/balances", response_model=List[CurrencyBalanceModel])
async def get_balances(
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
    limit: Optional[int] = 100,
):
    return await read_all_balances(database, limit)


@router.put("/balances/refresh")
async def refresh_balances(
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
):
    bottify_worker.send_task("core.worker.update_user_balances", args=[user.id])

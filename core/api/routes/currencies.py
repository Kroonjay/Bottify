import logging
from pydantic import ValidationError
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from databases import Database
from typing import Optional, List

from core.models.user import BottifyUserModel
from core.security.login_helpers import authenticate_user
from core.database.database import get_db
from core.models.currency import CurrencyCreateModel, CurrencyInModel, CurrencyModel
from core.database.crud.currency import (
    create_currency,
    read_all_currencies,
    read_currency_by_id,
)


router = APIRouter()


@router.post("/currency/create")
async def post_currency(
    currency_in: CurrencyCreateModel,
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
):
    try:
        cim = CurrencyInModel(**currency_in.dict())
        success = await create_currency(database, cim)
    except ValidationError as ve:
        logging.error(f"Post Currency : ValidationError : Data {ve.json()}")
        success = False
    return JSONResponse(content={"success": success})


@router.get("/currency/{currency_id}", response_model=CurrencyModel)
async def get_currency(
    currency_id: int,
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
):
    return await read_currency_by_id(database, currency_id)


@router.get("/currencies", response_model=List[CurrencyModel])
async def get_currencies(
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
    limit: Optional[int] = 100,
):
    return await read_all_currencies(database, limit)

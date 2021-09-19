import logging
from pydantic import ValidationError
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from databases import Database
from typing import Optional, List
from core.worker import bottify_worker
from core.models.user import BottifyUserModel
from core.security.login_helpers import authenticate_user, authenticate_god, user_is_god
from core.database.database import get_db
from core.enums.statuses import BottifyStatus
from core.models.exchange import (
    ExchangeInModel,
    ExchangeModel,
    ExchangeApiModel,
    ExchangeCreateModel,
)
from core.models.market import MarketModel
from core.database.crud.market import read_markets_by_exchange
from core.database.crud.exchange import (
    create_exchange,
    read_all_exchanges,
    read_exchange_by_id,
    read_active_exchanges_by_user,
)


router = APIRouter()


@router.post("/exchange/create")
async def post_exchange(
    exchange_in: ExchangeCreateModel,
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
):
    try:
        eim = ExchangeInModel(**exchange_in.dict(), user_id=user.id)
    except ValidationError as ve:
        logging.error(f"Post Exchange : ValidationError : {ve.json()}")
        return JSONResponse(content={"success": False})
    created = await create_exchange(database, eim)
    if not created:
        raise HTTPException(
            status_code=400,
            detail="Failed to Create Exchange - Likely due to a Duplicate Unique Value",
        )
    return JSONResponse(content={"success": created})


@router.get("/exchange/{exchange_id}", response_model=ExchangeApiModel)
async def get_exchange(
    exchange_id: int,
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
):
    return await read_exchange_by_id(database, exchange_id)


@router.get("/exchanges", response_model=List[ExchangeApiModel])
async def get_exchanges(
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
    limit: Optional[int] = 100,
):
    if user_is_god(
        user
    ):  # Only God can see all Exchanges, all other Users can only see their Exchanges tied to their user_id
        exchanges = await read_all_exchanges(database, limit)
    else:
        exchanges = await read_active_exchanges_by_user(database, user.id)
    if not exchanges:
        return []
    return [(ExchangeApiModel(**exchange.dict())) for exchange in exchanges]


@router.get("/exchange/{exchange_id}/markets", response_model=List[MarketModel])
async def get_exchange_markets(
    exchange_id: int,
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
    limit: Optional[int] = 100,
):
    return await read_markets_by_exchange(database, exchange_id, limit)


@router.put("/exchange/{exchange_id}/markets/refresh")
async def update_exchange_markets(
    exchange_id: int,
    user: BottifyUserModel = Depends(authenticate_god),
    database: Database = Depends(get_db),
):
    exchange = await read_exchange_by_id(database, exchange_id)
    if not exchange.status == BottifyStatus.Active:
        return JSONResponse(
            content={
                "success": False,
                "detail": f"Exchange must have Active Status, Got: {exchange.status.name}",
            }
        )
    bottify_worker.send_task("core.worker.update_exchange_markets", args=[exchange.id])
    return JSONResponse(content={"success": True, "detail": None})

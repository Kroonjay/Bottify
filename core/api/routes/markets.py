import logging
from pydantic import ValidationError
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from databases import Database
from typing import Optional, List
from core.worker import bottify_worker
from core.models.user import BottifyUserModel
from core.security.login_helpers import authenticate_user, authenticate_god
from core.database.database import get_db
from core.models.market import MarketInModel, MarketModel, MarketCreateModel
from core.database.crud.market import (
    create_market,
    read_all_markets,
    read_market_by_id,
    read_markets_by_exchange,
)


router = APIRouter()


@router.post("/market/create")
async def post_market(
    market_create: MarketCreateModel,
    user: BottifyUserModel = Depends(authenticate_god),
    database: Database = Depends(get_db),
):
    try:
        market_in = MarketInModel(**market_create.dict())
    except ValidationError as ve:
        logging.error(f"Post Market : MarketInModel : ValidationError : {ve.json()}")
        raise HTTPException(
            status_code=400,
            detail="Failed to Create Market - Input Data is Missing or Invalid",
        )
    created = await create_market(database, market_in)
    if not created:
        raise HTTPException(
            status_code=400,
            detail="Failed to Create Market - Likely due to a Duplicate Unique Value",
        )
    return JSONResponse(content={"success": created})


@router.get("/market/{market_id}", response_model=MarketModel)
async def get_market(
    market_id: int,
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
):
    return await read_market_by_id(database, market_id)


@router.get("/markets", response_model=List[MarketModel])
async def get_markets(
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
    limit: Optional[int] = 100,
):
    return await read_all_markets(database, limit)


@router.get("/markets/exchange/{exchange_id}", response_model=List[MarketModel])
async def get_exchange_markets(
    exchange_id: int, database: Database = Depends(get_db), limit: Optional[int] = 100
):
    return await read_markets_by_exchange(database, exchange_id, limit)


@router.put("/markets/refresh")
async def refresh_markets(
    user: BottifyUserModel = Depends(authenticate_god),
    database: Database = Depends(get_db),
):
    bottify_worker.send_task("core.worker.update_all_markets")
    return JSONResponse(content={"success": True})

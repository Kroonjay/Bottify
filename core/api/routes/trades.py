import logging
from pydantic import ValidationError
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from databases import Database
from typing import Optional, List

from core.models.user import BottifyUserModel
from core.security.login_helpers import authenticate_user
from core.database.database import get_db
from core.models.trade import TradeInModel, TradeModel
from core.database.crud.trade import (
    create_trade,
    read_all_trades,
    read_trade_by_id,
)


router = APIRouter()


@router.post("/trade/create")
async def post_trade(
    trade_in: TradeInModel,
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
):
    created = await create_trade(database, trade_in)
    if not created:
        raise HTTPException(
            status_code=400,
            detail="Failed to Create Trade - Likely due to a Duplicate Unique Value",
        )
    return JSONResponse(content={"success": created})


@router.get("/trade/{trade_id}", response_model=TradeModel)
async def get_trade(
    trade_id: int,
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
):
    return await read_trade_by_id(database, trade_id)


@router.get("/trades", response_model=List[TradeModel])
async def get_trades(
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
    limit: Optional[int] = 100,
):
    return await read_all_trades(database, limit)

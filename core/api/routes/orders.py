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
from core.models.order import (
    BottifyOrderInModel,
    BottifyOrderModel,
    BottifyOrderCreateModel,
)
from core.database.crud.bottify_order import (
    create_order,
    read_all_orders,
    read_order_by_id,
)


router = APIRouter()


@router.post("/order/create")
async def post_order(
    order_in: BottifyOrderCreateModel,
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
):

    bottify_worker.send_task("core.worker.place_order", args=[order_in.json()])
    return JSONResponse(content={"success": True})


@router.get("/order/{order_id}", response_model=BottifyOrderModel)
async def get_order(
    order_id: int,
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
):
    return await read_order_by_id(database, order_id)


@router.get("/orders", response_model=List[BottifyOrderModel])
async def get_orders(
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
    limit: Optional[int] = 100,
):
    return await read_all_orders(database, limit)


@router.get("/orders/sync")
async def refresh_orders(
    user: BottifyUserModel = Depends(authenticate_god),
    database: Database = Depends(get_db),
):
    bottify_worker.send_task("core.worker.refresh_open_orders")
    return JSONResponse(content={"success": True})

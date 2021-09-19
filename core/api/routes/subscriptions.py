import logging
from pydantic import ValidationError
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from databases import Database
from typing import Optional, List

from core.models.user import BottifyUserModel
from core.security.login_helpers import authenticate_user, user_is_god
from core.database.database import get_db
from core.models.subscription import SubscriptionInModel, SubscriptionModel
from core.database.crud.subscription import (
    read_subscription_by_id,
    read_all_subscriptions,
    create_subscription,
)
from core.database.crud.strategy import read_user_strategies

router = APIRouter()


@router.post("/subscription/create")
async def post_subscription(
    subscription_in: SubscriptionInModel,
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
):

    success = await create_subscription(database, subscription_in)
    return JSONResponse(content={"success": success})


@router.get("/subscriptions", response_model=List[SubscriptionModel])
async def get_subscriptions(
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
    limit: Optional[int] = 100,
):
    return await read_all_subscriptions(database, limit)


@router.get("/subscription/{subscription_id}", response_model=SubscriptionModel)
async def get_subscription(
    subscription_id: int,
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
):
    return await read_subscription_by_id(database, subscription_id)

import logging
from fastapi import APIRouter, Depends, status, HTTPException
from databases import Database
from typing import List, Optional
from uuid import UUID
from pydantic import ValidationError
from core.database.database import get_db
from core.models.user import BottifyUserModel
from core.models.subscription import SubscriptionModel
from core.security.login_helpers import authenticate_user, user_is_god
from core.models.strategy import StrategyInModel, StrategyModel, StrategyCreateModel
from core.database.crud.currency import read_currency_by_symbol
from core.database.crud.strategy import (
    create_strategy,
    read_strategy_by_guid,
    read_all_strategies,
    read_user_strategies,
)
from core.database.crud.subscription import (
    read_subscriptions_by_strategy_id,
)

router = APIRouter()


@router.post("/strategy/create", response_model=StrategyModel)
async def post_strategy(
    strategy_in: StrategyCreateModel,
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
):
    base_currency = await read_currency_by_symbol(database, strategy_in.base_currency)
    if not base_currency:
        logging.error(
            f"Post Strategy : Invalid Base Currency : Symbol {str(strategy_in.base_currency)}"
        )
        raise HTTPException(
            status_cude=400, detail="Strategy Base Currency is Missing or Invalid"
        )
    try:
        sim = StrategyInModel(
            **strategy_in.dict(exclude={"base_currency"}),
            user_id=user.id,
            base_currency_id=base_currency.id,
        )
    except ValidationError as ve:
        logging.error(
            f"Create Strategy:Failed to Validate StrategyInModel:Data: {ve.json()}"
        )
        raise HTTPException(status_code=400, detail="Failed to Validate Strategy")

    created = await create_strategy(database, sim)
    if not created:
        raise HTTPException(
            status_code=400,
            detail="Failed to Create Strategy - Likely due to a Duplicate Unique Value",
        )
    strategy = await read_strategy_by_guid(database, sim.guid)
    if not strategy:
        raise HTTPException(
            status_code=404, detail="Failed To Retrieve Strategy After Creation"
        )
    return strategy


@router.get("/strategies", response_model=List[StrategyModel])
async def get_strategies(
    limit: Optional[int] = 100,
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
):
    strategies = []
    if user_is_god(user):
        return await read_all_strategies(database, limit)
    else:
        return await read_user_strategies(database, user.id)


@router.get("/strategy/{strategy_guid}", response_model=StrategyModel)
async def get_strategy(
    strategy_guid: UUID,
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
):
    # try:
    #     strategy_guid = UUID(strategy_guid)
    # except ValueError as ve:
    #     logging.error(
    #         f"Get Strategy:Strategy GUID Must be valid UUID:Got: {str(strategy_guid)}:Data: {ve.args}"
    #     )
    #     raise HTTPException(status_code=400, detail="Strategy GUID is Invalid")
    return await read_strategy_by_guid(database, strategy_guid)


@router.get(
    "/strategies/{strategy_guid}/subscriptions",
    response_model=List[SubscriptionModel],
)
async def get_strategy(
    strategy_guid: UUID,
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
):
    strategy = await read_strategy_by_guid(database, strategy_guid)
    if not strategy:
        raise HTTPException(status_code=400, detail="No Strategy Found for GUID")
    if user_is_god(user):
        return await read_subscriptions_by_strategy_id(database, strategy.id)
    else:
        if strategy.user_id == user.id:
            return await read_subscriptions_by_strategy_id(database, strategy.id)
        else:
            raise HTTPException(
                status_code=403, detail="This Strategy Doesn't Belong to You"
            )

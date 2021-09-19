import logging
from pydantic import ValidationError
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from databases import Database
from typing import Optional, List

from core.models.user import BottifyUserModel
from core.security.login_helpers import authenticate_user, user_is_god
from core.database.database import get_db

from core.models.reaction import ReactionCreateModel, ReactionInModel, ReactionModel
from core.database.crud.reaction import (
    read_reaction_by_id,
    read_reactions_by_alert_type,
    read_reactions_by_monitor_id,
    read_all_reactions,
    create_reaction,
)
from core.database.crud.strategy import read_user_strategies

router = APIRouter()


@router.post("/reaction/create")
async def post_reaction(
    reaction_in: ReactionCreateModel,
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
):
    try:
        rim = ReactionInModel(**reaction_in.dict())
        success = await create_reaction(database, rim)
    except ValidationError as ve:
        logging.error(f"Post Reaction : ValidationError : Data {ve.json()}")
        success = False
    return JSONResponse(content={"success": success})


@router.get("/reactions", response_model=List[ReactionModel])
async def get_reactions(
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
    limit: Optional[int] = 100,
):
    return await read_all_reactions(database, limit)


@router.get("/reaction/{reaction_id}", response_model=ReactionModel)
async def get_reaction(
    reaction_id: int,
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
):
    return await read_reaction_by_id(database, reaction_id)

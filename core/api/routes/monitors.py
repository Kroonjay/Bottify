import logging


from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from databases import Database
from typing import List, Optional
from core.config import ALERT_SECRET_KEY
from core.worker import bottify_worker
from core.database.database import get_db
from core.models.user import BottifyUserModel
from core.enums.statuses import BottifyStatus
from core.database.crud.strategy import read_user_strategies
from core.database.crud.monitor import (
    create_monitor,
    read_all_monitors,
    read_monitor_by_id,
)

from core.security.login_helpers import authenticate_user, user_is_god, authenticate_god
from core.models.monitor import (
    MonitorInModel,
    MonitorModel,
)


router = APIRouter()


@router.get("/monitors", response_model=List[MonitorModel])
async def get_monitors(
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
    limit: Optional[int] = 100,
):
    return await read_all_monitors(database, limit)


# Monitor Creation Not Yet Supported
@router.post("/monitor/create")
async def post_monitor(
    monitor_in: MonitorInModel,
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
):
    created = await create_monitor(database, monitor_in)
    if not created:
        raise HTTPException(
            status_code=400,
            detail="Failed to Create Indicator - Likely due to a Duplicate Unique Value",
        )
    return JSONResponse(content={"detail": "Success"})


@router.get("/monitor/{monitor_id}", response_model=MonitorModel)
async def get_monitor(
    monitor_id: int,
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
):
    return await read_monitor_by_id(database, monitor_id)


@router.put("/monitor/create/sync")
async def get_monitor(
    monitor_source_id: str,
    user: BottifyUserModel = Depends(authenticate_god),
    database: Database = Depends(get_db),
):
    bottify_worker.send_task("core.worker.sync_monitor", args=[monitor_source_id])
    return JSONResponse(content={"success": True, "detail": "Monitor Sync Started"})

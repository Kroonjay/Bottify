import logging
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from databases import Database
from typing import Optional, List
from pydantic import ValidationError

from core.models.user import BottifyUserModel
from core.security.login_helpers import authenticate_user, authenticate_god
from core.models.feed import (
    FeedInModel,
    FeedModel,
    FeedCreateModel,
    FeedApiModel,
    FeedWorkerModel,
)
from core.database.database import get_db
from core.database.crud.feeds import (
    create_feed,
    read_feed_by_id,
    read_all_feeds,
    read_overdue_active_feeds,
    update_feed_configs,
)
from core.database.tables.feeds import get_feeds_table
from core.worker import bottify_worker

router = APIRouter()

feed_table = get_feeds_table()


@router.post("/feed/create")
async def post_feed(
    feed_in: FeedCreateModel,
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
):
    try:
        fim = FeedInModel(**feed_in.dict())
        success = await create_feed(database, fim)
    except ValidationError as ve:
        logging.error(f"Post User : ValidationError : Data {ve.json()}")
        success = False
    return JSONResponse(content={"success": success})


@router.get("/feeds", response_model=List[FeedApiModel])
async def get_feeds(
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
    limit: Optional[int] = 100,
):
    feeds = await read_all_feeds(database, limit)
    if not feeds:
        return []
    return [(FeedApiModel(**feed.dict())) for feed in feeds]


@router.get("/feed/{feed_id}", response_model=FeedApiModel)
async def get_feed(
    feed_id: int,
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
):
    feed = await read_feed_by_id(database, feed_id)
    if not feed:
        logging.error(f"Get Feed : No Result : Feed ID {feed_id}")
        return None
    else:
        return FeedApiModel(**feed.dict())


@router.get("/feed/{feed_id}/refresh")
async def refresh_feed(
    feed_id: int,
    user: BottifyUserModel = Depends(authenticate_god),
    database: Database = Depends(get_db),
):
    feed = await read_feed_by_id(database, feed_id)
    if not feed:
        raise HTTPException(status_code=400, detail="Refresh Failed - Feed is Invalid")
    try:
        fwm = FeedWorkerModel(**feed.dict())
        logging.error(fwm.json())
    except ValidationError as ve:
        logging.error(f"Refresh Feed : ValidationError : {ve.json()}")
        raise HTTPException(status_code=400, detail="Refresh Failed - Feed is Invalid")
    bottify_worker.send_task("core.worker.refresh_feed", args=[fwm.json()])


@router.get("/feeds/overdue", response_model=List[FeedApiModel])
async def get_overdue_feeds(database: Database = Depends(get_db)):
    overdue_feeds = await read_overdue_active_feeds(database)
    out_feeds = []
    for feed in overdue_feeds:
        out_feeds.append(FeedApiModel(**feed.dict()))
    return out_feeds
    # Using a Dict comprehension will throw an assertion here when calling dict method


@router.put("/feed/{feed_id}/configs")
async def put_feed_configs(
    feed_id: int,
    configs: dict,
    user: BottifyUserModel = Depends(authenticate_god),
    database: Database = Depends(get_db),
):
    feed = await read_feed_by_id(database, feed_id)
    if not feed:
        raise HTTPException(status_code=404, detail="Feed Not Found")
    success = await update_feed_configs(database, feed_id, configs)
    return JSONResponse(content={"success": success})

import logging

from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.responses import JSONResponse
from databases import Database
from typing import Optional, List
from core.config import settings
from core.enums.statuses import BottifyStatus
from core.database.database import get_db
from core.database.crud.alert import read_all_alerts, create_alert, read_alert_by_id
from core.database.crud.monitor import read_monitor_by_source_id
from core.database.crud.subscription import read_subscriptions_by_monitor_id
from core.models.alert import AlertInModel, AlertModel, AlertCreateModel
from core.models.user import BottifyUserModel
from core.security.login_helpers import authenticate_user, user_is_god, authenticate_god
from core.worker import bottify_worker

router = APIRouter()


def alert_secret_key_is_valid(sk_in: str):
    return True if sk_in == settings.AlertSecretKey else False


@router.post("/alert/hook")
async def indicator_alert_webhook(
    alert_in: AlertCreateModel,
    x_bottify_sec: Optional[str] = Header(None),
    database: Database = Depends(get_db),
):
    if not x_bottify_sec:
        logging.error(f"Indicator Alert Webhook:Bottify Security Header Not Present")
        raise HTTPException(
            status_code=400,
            detail="It's Unclear What You're Trying to do...But it didn't work.",
        )
    if not alert_secret_key_is_valid(x_bottify_sec):
        logging.error(
            f"Indicator Alert Webhook:Bottify Security Header is Invalid:Value: {str(x_bottify_sec)}"
        )
        raise HTTPException(
            status_code=400,
            detail="It's Unclear What You're Trying to do...But it didn't work.",
        )
    monitor = await read_monitor_by_source_id(database, alert_in.source_id)
    if not monitor:
        logging.error(
            f"Alert Webhook : No Monitor Found for Source ID : Source ID {str(alert_in.source_id)}"
        )
        raise HTTPException(
            status_code=400, detail="Alert Source ID is Missing or Invalid"
        )
    if not monitor.status == BottifyStatus.Active:
        raise HTTPException(
            status_code=400,
            detail=f"Received Alert for Invalid Monitor : Monitor is Inactive",
        )

    try:
        new_alert = AlertInModel(**alert_in.dict(), monitor_id=monitor.id)
    except ValidationError as ve:
        logging.error(f"Alert Webhook : AlertInModel : ValidationError : {ve.json()}")
        raise HTTPException(
            status_code=400,
            detail=f"Received Alert for Invalid Monitor : Invalid Alert Format",
        )
    success = await create_alert(database, new_alert)
    if not success:
        raise HTTPException(status_code=400, detail=f"Failed to Create Alert")
    subscriptions = await read_subscriptions_by_monitor_id(database, monitor.id)
    for subscription in subscriptions:
        params = {
            "reaction_id": subscription.reaction_id,
            "strategy_id": subscription.strategy_id,
            "alert_in": new_alert.json(),
        }
        bottify_worker.send_task(
            "core.worker.handle_reaction", kwargs=params, queue="trade_tasks"
        )
    return JSONResponse(content={"success": success})


@router.get("/alerts", response_model=List[AlertModel])
async def get_alerts(
    user: BottifyUserModel = Depends(authenticate_god),
    database: Database = Depends(get_db),
    limit: Optional[int] = 100,
):
    return await read_all_alerts(database, limit)


@router.get("/alert/{alert_id}", response_model=AlertModel)
async def get_alert(
    alert_id: int,
    user: BottifyUserModel = Depends(authenticate_user),
    database: Database = Depends(get_db),
):
    return await read_alert_by_id(database, alert_id)

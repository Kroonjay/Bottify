from core.elasticsearch.api import ElasticApiHelper
from core.database.database import create_db
from core.models.monitor import MonitorInModel
from core.database.crud.monitor import (
    read_monitor_by_source_id,
    create_monitor,
    update_monitor,
)
import logging
from pydantic import ValidationError

logger = logging.getLogger("Bottify.Tasks.Monitor")


async def async_work_refresh_monitor(monitor_source_id: str):
    eah = ElasticApiHelper()
    async with create_db() as database:
        new_monitor = eah.get_monitor(monitor_source_id)
        if not new_monitor:
            logger.error(
                f"Async Work Refresh Monitor : No Elastic Monitor Found for ID : Source ID {monitor_source_id}"
            )
            return
        try:
            monitor_in = MonitorInModel(**new_monitor.dict())
        except ValidationError as ve:
            logger.error(
                f"Async Work Refresh Monitor : MonitorInModel : ValidationError : {ve.json()}"
            )
            return
        db_monitor = await read_monitor_by_source_id(database, monitor_in.source_id)
        if not db_monitor:
            logger.info(
                f"Async Work Sync Monitor : No Monitor Found for Source ID, Attempting to Create : Source ID {monitor_source_id}"
            )
            success = await create_monitor(database, monitor_in)
            if not success:
                logger.error(
                    "Async Work Refresh Monitor : Failed to Create Monitor in Database"
                )
            return
        else:
            updated_monitor = db_monitor.copy(
                update=monitor_in.dict(exclude={"monitor_id"}, exclude_defaults=True)
            )
            success = await update_monitor(database, updated_monitor)
            if not success:
                logger.error(
                    f"Async Work Refresh Monitor : Failed to Update Monitor in Database"
                )

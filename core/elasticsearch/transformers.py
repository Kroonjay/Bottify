from core.models.monitor import MonitorCreateModel
from core.enums.statuses import BottifyStatus
from core.enums.alert_severity import AlertSeverity
from datetime import timedelta
from pydantic import ValidationError
import logging


def transform_monitor_alert_schedule(monitor_data):
    schedule = monitor_data.get("schedule")
    if not schedule:
        logging.error(
            "Transform Monitor Alert Schedule : Monitor Missing Required Key : Schedule"
        )
        return None
    period = schedule.get("period")
    if not period:
        logging.error(
            "Transform Monitor Alert Schedule : Schedule Missing Required Key : Period"
        )
        return None
    if period.get("unit") == "MINUTES":
        return period.get("interval")
    else:
        logging.error(
            f"Transform Monitor Alert Schedule : Schedule Period Unit is Unsupported : Unit {period.get('unit')}"
        )
        return None


def transform_monitor_status(monitor_data):
    if monitor_data.get("enabled"):
        return BottifyStatus.Active
    else:
        return BottifyStatus.SourceDisabled


def transform_monitor_alert_severity(monitor_data):
    triggers = monitor_data.get("triggers")
    if not triggers:
        logging.error(
            "Transform Monitor Alert Severity : Monitor Missing Required Key : Triggers"
        )
        return AlertSeverity.Unset
    for trigger in triggers:
        severity = trigger.get("severity")
        if severity:
            return severity
    logging.error(
        "Transform Monitor Alert Severity : All Monitor Triggers Missing Required Key : Severity"
    )
    return AlertSeverity.Unset


def transform_monitor_input_indices(monitor_data):
    indices = []
    inputs = monitor_data.get("inputs")
    if not inputs:
        logging.error(
            f"Transform Monitor Input Indices : Monitor Missing Required Key : Inputs"
        )
        return indices
    for item in inputs:
        search = item.get("search")
        if not search:
            logging.error(
                "Transform Monitor Input Indices : Input Missing Required Key : Search"
            )
            continue
        item_indices = search.get("indices")
        if not item_indices:
            logging.error(
                "Transform Monitor Input Indices : Search Input Missing Required Key : Indices"
            )
            continue
        indices.extend(item_indices)
    if not indices:
        logging.error(
            f"Transform Monitor Input Indices : No Indices : Data {monitor_data}"
        )
    return indices


def transform_monitor_input_queries(monitor_data):
    queries = []
    inputs = monitor_data.get("inputs")
    if not inputs:
        logging.error(
            f"Transform Monitor Input Queries : Monitor Missing Required Key : Inputs"
        )
        return queries
    for item in inputs:
        search = item.get("search")
        if not search:
            logging.error(
                "Transform Monitor Input Queries : Input Missing Required Key : Search"
            )
            continue
        query = search.get("query")
        if not query:
            logging.error(
                f"Transform Monitor Input Queries : Search Input Missing Required Key : Query"
            )
            continue
        queries.append(query)
    if not queries:
        logging.error(
            f"Transform Monitor Input Queries : No Queries : Data {monitor_data}"
        )
    return queries


def transform_monitor(monitor):
    monitor_data = monitor.get("monitor")
    if not monitor_data:
        logging.error("Transform Monitor : Monitor Missing Required Key : Monitor")
        return None
    try:
        return MonitorCreateModel(
            name=monitor_data.get("name"),
            source_id=monitor.get("_id"),
            status=transform_monitor_status(monitor_data),
            severity=transform_monitor_alert_severity(monitor_data),
            indices=transform_monitor_input_indices(monitor_data),
            queries=transform_monitor_input_queries(monitor_data),
            definition=monitor_data,
            updated_at=monitor_data.get("last_update_time"),
        )
    except ValidationError as ve:
        logging.error(
            f"Transform Monitor : MonitorCreateModel : ValidationError : {ve.json()}"
        )
        return None


# UNFINISHED
def transform_model_to_mapping(model):

    map_name = None
    map_type = None
    if not isinstance(model, BaseModel):
        logging.error(
            f"Transform Model to Mapping : Model must be inherit BaseModel, Got {type(model)}"
        )
        return None
    schema = model.schema()

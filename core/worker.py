import asyncio
import logging
import requests
from celery import Celery
from kombu import Queue
from typing import List, Dict, Optional
from pydantic import ValidationError, BaseModel
from asgiref.sync import async_to_sync
from core.enums.orders import OrderDirection, OrderTimeInForce, OrderType
from core.models.order import BottifyOrderCreateModel, BottifyOrderInModel
from core.models.alert import AlertInModel
from core.engine.trades import async_work_place_trade
from core.engine.balances import (
    async_work_update_exchange_balances,
    async_work_update_user_balances,
)
from core.engine.markets import (
    async_work_update_exchange_markets,
    async_work_update_all_markets,
)
from core.engine.alerts import async_work_handle_reaction
from core.engine.orders import async_work_place_order, async_work_refresh_open_orders
from core.engine.monitor import async_work_refresh_monitor
from datetime import datetime, timedelta
from databases import Database
from core.database.database import get_db, create_db
from core.engine.feeds import async_work_refresh_feed
from core.models.feed import FeedWorkerModel
from core.database.crud.feeds import (
    read_feed_by_id,
    update_feed_refresh_started,
    update_feed_refresh_complete,
    read_active_feeds,
    read_overdue_active_feeds,
)
from core.database.crud.exchange import (
    read_exchange_by_id,
    read_active_exchanges_by_user,
)
from core.database.crud.bottify_order import create_order
from core.database.crud.balance import (
    read_balance_by_currency_exchange,
    create_balance,
    update_balance,
)
from core.database.crud.market import read_market_by_id
from core.config import (
    CELERY_WORKER_NAME,
    CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND_URL,
    MAIN_DB_CONN_STRING,
)
from core.elasticsearch.utils import bulk_index
import nest_asyncio  # Required in order to call and execute async tasks from inside a running event loop

nest_asyncio.apply()

bottify_worker = Celery(CELERY_WORKER_NAME)
bottify_worker.conf.broker_url = CELERY_BROKER_URL
bottify_worker.result_backend = CELERY_RESULT_BACKEND_URL
bottify_worker.task_default_queue = "main"
bottify_worker.conf.task_queues = (
    Queue("main"),
    Queue("trade_tasks"),
    Queue("feed_tasks"),
)
bottify_worker.conf.task_routes = {
    "core.worker.refresh_feed": {
        "queue": "feed_tasks",
    },
    "core.worker.refresh_user_balances": {
        "queue": "trade_tasks",
    },
    "core.worker.refresh_all_markets": {"queue": "main"},
    "core.worker.place_order": {"queue": "trade_tasks"},
    "core.worker.handle_reaction": {"queue": "trade_tasks"},
    "core.worker.refresh_open_orders": {
        "queue": "trade_tasks",
    },
    "core.worker.refresh_overdue_feeds": {"queue": "main"},
}

bottify_worker.task_default_exchange_type = "direct"
bottify_worker.autodiscover_tasks()


@bottify_worker.task()
def refresh_feed(feed_id: int):

    if isinstance(feed_id, list):
        feed_id = feed_id[0]
    loop = asyncio.new_event_loop()
    loop.run_until_complete(async_work_refresh_feed(feed_id))
    logging.info(f"Refresh Feed : Feed ID {feed_id}")


@bottify_worker.task()
def refresh_exchange_balances(exchange_id: int):
    if isinstance(exchange_id, list):
        exchange_id = exchange_id[0]
    success = asyncio.run(async_work_update_exchange_balances(exchange_id))


@bottify_worker.task()
def refresh_user_balances(user_id: int):
    if isinstance(user_id, list):
        user_id = user_id[0]
    success = asyncio.run(async_work_update_user_balances(user_id))


@bottify_worker.task()
def refresh_all_markets():
    asyncio.run(async_work_update_all_markets())


@bottify_worker.task()
def place_order(order_in: str):
    if isinstance(order_in, list):
        order_in = order_in[0]
    try:
        new_order = BottifyOrderCreateModel.parse_raw(order_in)
    except ValidationError as ve:
        logging.error(
            f"Place Order : BottifyOrderCreateModel : ValidationError : {ve.json()}"
        )
        return
    asyncio.run(async_work_place_order(new_order))


@bottify_worker.task()
def sync_monitor(monitor_source_id: str):
    if isinstance(
        monitor_source_id, list
    ):  # Doing this allows the task to work with both args and kwargs
        monitor_source_id = monitor_source_id[0]
    asyncio.run(async_work_refresh_monitor(monitor_source_id))


@bottify_worker.task()
def handle_reaction(reaction_id: int, strategy_id: int, alert_in: str):
    try:
        alert = AlertInModel.parse_raw(alert_in)
    except ValidationError as ve:
        logging.error(f"Handle Reaction : AlertInModel : ValidationError : {ve.json()}")
        return
    asyncio.run(async_work_handle_reaction(reaction_id, strategy_id, alert))


@bottify_worker.task()
def refresh_open_orders():
    asyncio.run(async_work_refresh_open_orders())


@bottify_worker.task()
def refresh_overdue_feeds():
    response = requests.get("http://127.0.0.1:8000/api/v1/feeds/overdue", timeout=30)
    feed_count = 0
    for feed in response.json():
        feed_count += 1
        params = {"feed_id": feed["id"]}
        bottify_worker.send_task(
            "core.worker.refresh_feed", kwargs=params, queue="feed_tasks"
        )
    logging.info(f"Refresh Overdue Feeds : Complete : Refreshed {feed_count} Feeds")


bottify_worker.conf.beat_schedule = {
    "refresh-open-orders": {
        "task": "core.worker.refresh_open_orders",
        "schedule": 60.0,
    },
    "refresh-markets": {"task": "core.worker.refresh_all_markets", "schedule": 600.0},
    "refresh_overdue_feeds": {
        "task": "core.worker.refresh_overdue_feeds",
        "schedule": 60.0,
    },
}

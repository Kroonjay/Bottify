from fastapi import APIRouter, Depends
from core.api.routes import (
    login,
    monitors,
    strategies,
    alerts,
    feeds,
    currencies,
    balances,
    trades,
    markets,
    orders,
    exchanges,
    subscriptions,
    reactions,
    budgets,
)

# Import all routes and add them to router
api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(monitors.router)
api_router.include_router(strategies.router)
api_router.include_router(alerts.router)
api_router.include_router(feeds.router)
api_router.include_router(currencies.router)
api_router.include_router(balances.router)
api_router.include_router(markets.router)
api_router.include_router(exchanges.router)
api_router.include_router(orders.router)
api_router.include_router(trades.router)
api_router.include_router(reactions.router)
api_router.include_router(subscriptions.router)
api_router.include_router(budgets.router)

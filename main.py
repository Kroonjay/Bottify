from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from databases import Database
import uvicorn

from core.api.api import api_router
from core.database.database import get_db
from core.config import (
    PROJECT_NAME,
    SERVER_HOST,
    SERVER_PORT,
    DEBUG_ENABLED,
    API_ROUTER_PREFIX,
    TOKEN_URL_PREFIX,
    OPENAPI_URL_PREFIX,
)

app = FastAPI(title=PROJECT_NAME, openapi_url=OPENAPI_URL_PREFIX)
app.include_router(api_router, prefix=API_ROUTER_PREFIX)


@app.on_event("startup")
async def startup():
    database = get_db()
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    database = get_db()
    await database.disconnect()


def main():
    uvicorn.run(
        app, host=SERVER_HOST, port=SERVER_PORT, debug=DEBUG_ENABLED, reload=True
    )


if __name__ == "__main__":
    main()

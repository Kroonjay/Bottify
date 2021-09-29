from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from databases import Database
import uvicorn

from core.api.api import api_router
from core.database.database import get_db
from core.config import settings

app = FastAPI(title=settings.ProjectName, openapi_url=settings.OpenApiUrlPrefix)
app.include_router(api_router, prefix=settings.ApiPrefix)


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
        app,
        host=str(settings.ServerHost),
        port=settings.Port,
        debug=settings.DebugEnabled,
    )


if __name__ == "__main__":
    main()

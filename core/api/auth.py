from fastapi import HTTPException, Security, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.status import HTTP_403_FORBIDDEN
from databases import Database
from pydantic import ValidationError
from datetime import datetime, timedelta
import secrets
import jwt
import logging

from core.database.database import get_db
from core.database.crud.bottify_user import read_user_by_guid

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/token")


async def authenticate_user(
    token: str = Security(reusable_oauth2), database: Database = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
    except jwt.PyJWTError as e:
        log_str = f"UserToken Decode Error::{e.args[0]}"
        logging.error(log_str)
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    user = await database.fetch_one(
        read_user_by_name, values={"username": token_data.username}
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.isActive:
        raise HTTPException(status_code=403, detail="User Inactive")
    return user

import jwt
import logging
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from starlette.status import HTTP_403_FORBIDDEN
from fastapi import HTTPException, Security, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from databases import Database
from core.config import (
    JWT_ALGORITHM,
    JWT_SUBJECT,
    TOKEN_URL_PREFIX,
    PASSWORD_HASH_SCHEME,
)
from core.security.keys import JWT_PRIVATE_KEY, JWT_PUBLIC_KEY
from core.models.token import TokenPayload
from core.database.crud.bottify_user import read_user_by_guid
from core.models.user import BottifyUserModel
from core.database.database import get_db
from core.enums.statuses import BottifyStatus
from core.enums.roles import UserRole

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=TOKEN_URL_PREFIX)

pwd_context = CryptContext(schemes=[PASSWORD_HASH_SCHEME])


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(tz=timezone.utc) + expires_delta
    else:
        expire = datetime.now(tz=timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire, "sub": JWT_SUBJECT})
    encoded_jwt = jwt.encode(to_encode, JWT_PRIVATE_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


async def authenticate_user(
    token: str = Security(reusable_oauth2), database: Database = Depends(get_db)
):
    try:
        payload = jwt.decode(token, JWT_PUBLIC_KEY, algorithms=[JWT_ALGORITHM])
        token_data = TokenPayload(**payload)
    except jwt.PyJWTError as e:
        logging.error(
            f"Authenticate User Error:Failed to Decode JWT Payload:Data: {e.args}"
        )
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="User Authentication Failed"
        )
    user = await read_user_by_guid(database, token_data.guid)
    if not user:
        logging.error(
            f"Authenticate User:Failed to Find User by Guid after Decoding Token:User GUID: {str(token_data.guid)}"
        )
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="User Authentication Failed"
        )
    if not user.status == BottifyStatus.Active:
        logging.error(
            f"Authenticate User:Received Request for Account without Active Status:User GUID: {str(user.guid)}"
        )
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="User Authentication Failed"
        )
    return user


def user_is_god(user: BottifyUserModel):
    return True if user.user_role == UserRole.God else False


def authenticate_god(
    user: BottifyUserModel = Depends(authenticate_user),
) -> BottifyUserModel:
    if not user_is_god(user):
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Only a God possesses these powers!"
        )
    return user

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from databases import Database

from core.security.login_helpers import create_access_token, verify_password
from core.database.database import get_db
from core.database.crud.bottify_user import read_user_by_guid, read_user_by_username
from core.database.tables.bottify_user import get_bottify_user_table
from core.models.user import BottifyUserModel
from core.models.token import Token, TokenPayload

router = APIRouter(prefix="/login")
users_table = get_bottify_user_table()


@router.post("/", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    database: Database = Depends(get_db),
):
    user = await read_user_by_username(database, form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Login Failure")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=400, detail="Login Failure:Invalid Username or Password"
        )
    token = Token(access_token=create_access_token(data={"guid": str(user.guid)}))
    return token

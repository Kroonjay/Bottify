from pydantic import BaseModel, validator
from uuid import uuid4, UUID
from datetime import datetime, timezone
from core.enums.statuses import BottifyStatus
from core.enums.roles import UserRole


class BottifyUserInModel(BaseModel):
    guid: UUID = None
    username: str
    password: str
    email: str
    status: int = None
    user_role: int = None  # Maps to UserPermissions object
    created_at: datetime = None

    @validator("guid", always=True)
    def set_user_guid(cls, v):
        return uuid4()

    @validator("username", always=True)
    def validate_username(cls, v):
        assert v.isalnum(), f"Username Must be Alphanumeric"
        return v

    @validator("status", always=True)
    def verify_status(cls, v):
        if isinstance(v, int):
            if v in BottifyStatus.__members__.values():
                return v
        if isinstance(v, BottifyStatus):
            return v.value
        return BottifyStatus.Active.value

    @validator("user_role", always=True)
    def verify_role(cls, v):
        if isinstance(v, int):
            if v in UserRole.__members__.values():
                return v
        if isinstance(v, UserRole):
            return v.value
        return UserRole.Unset.value

    @validator("created_at", always=True)
    def set_creation_time(cls, v):
        if isinstance(v, datetime):
            return v
        return datetime.now(tz=timezone.utc)


# TODO Add permissions to UserModel, not a priority until it actually works
class BottifyUserModel(BaseModel):
    id: int = None
    guid: UUID = None
    username: str = None
    hashed_password: str = None
    email: str = None
    status: BottifyStatus = BottifyStatus.Unset
    created_at: datetime = None
    user_role: UserRole = (
        UserRole.Unset
    )  # Role is a non-reserved keyword in PostgreSQL and most other DB languagges, best to avoid

    @validator("status", pre=True)
    def load_status(cls, v):
        if isinstance(v, int):
            if v in BottifyStatus.__members__.values():
                return BottifyStatus(v)
        if isinstance(v, BottifyStatus):
            return v
        print(
            f"ValidationError:UserModel:Failed to Load Status, using Default:Value: {v}"
        )
        return BottifyStatus.Unset

    @validator("user_role", pre=True)
    def load_user_role(cls, v):
        if isinstance(v, int):
            if v in UserRole.__members__.values():
                return UserRole(v)
        if isinstance(v, UserRole):
            return v
        print(
            f"ValidationError:UserModel:Failed to Load User Role, using Default:Value: {v}"
        )
        return UserRole.Unset

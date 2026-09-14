from datetime import date

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import ORMModel


class ClientRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str = Field(min_length=2, max_length=80)
    last_name: str = Field(min_length=2, max_length=80)
    phone: str | None = None
    birth_date: date | None = None


class ClientProfileUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=2, max_length=80)
    last_name: str | None = Field(default=None, min_length=2, max_length=80)
    phone: str | None = None
    birth_date: date | None = None


class ClientProfileRead(ORMModel):
    id: int
    user_id: int
    email: EmailStr
    first_name: str
    last_name: str
    phone: str | None = None
    birth_date: date | None = None
    points: int

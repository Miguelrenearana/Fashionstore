from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class CityRead(ORMModel):
    id: int
    name: str
    state: str


class CityCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    state: str = Field(min_length=2, max_length=100)


class CityUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    state: str | None = Field(default=None, min_length=2, max_length=100)


class BranchCreate(BaseModel):
    city_id: int
    name: str = Field(min_length=2, max_length=120)
    address: str = Field(min_length=4, max_length=255)
    phone: str | None = Field(default=None, max_length=20)


class BranchUpdate(BaseModel):
    city_id: int | None = None
    name: str | None = Field(default=None, min_length=2, max_length=120)
    address: str | None = Field(default=None, min_length=4, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    is_active: bool | None = None


class BranchRead(ORMModel):
    id: int
    city_id: int
    city: CityRead | None = None
    name: str
    address: str
    phone: str | None = None
    is_active: bool

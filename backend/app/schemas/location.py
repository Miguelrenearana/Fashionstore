from pydantic import BaseModel

from app.schemas.common import ORMModel


class CityRead(ORMModel):
    id: int
    name: str
    state: str


class BranchCreate(BaseModel):
    city_id: int
    name: str
    address: str
    phone: str | None = None


class BranchRead(ORMModel):
    id: int
    city_id: int
    city: CityRead | None = None
    name: str
    address: str
    phone: str | None = None
    is_active: bool

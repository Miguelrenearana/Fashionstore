from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class VariantCreate(BaseModel):
    size_id: int | None = None
    size_name: str | None = None
    color_id: int | None = None
    color_name: str | None = None
    sku: str = Field(min_length=3)
    price: float = Field(gt=0)


class GarmentCreate(BaseModel):
    category_id: int
    collection_id: int | None = None
    name: str = Field(min_length=2)
    description: str | None = None
    base_price: float = Field(gt=0)
    is_ar_enabled: bool = False
    variants: list[VariantCreate] = Field(default_factory=list)


class GarmentRead(ORMModel):
    id: int
    name: str
    description: str | None = None
    base_price: float
    is_ar_enabled: bool
    is_active: bool
    category_id: int


class VariantRead(ORMModel):
    id: int
    garment_id: int
    sku: str
    price: float
    size_id: int | None
    color_id: int | None


class GarmentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2)
    description: str | None = None
    base_price: float | None = Field(default=None, gt=0)
    is_ar_enabled: bool | None = None
    category_id: int | None = None
    collection_id: int | None = None
    is_active: bool | None = None

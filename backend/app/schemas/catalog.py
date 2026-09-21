
from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class CategoryRead(ORMModel):
    id: int
    name: str
    description: str | None = None
    is_active: bool


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = None


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = None
    is_active: bool | None = None


class SizeRead(ORMModel):
    id: int
    name: str


class SizeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=20)


class ColorRead(ORMModel):
    id: int
    name: str
    hex_code: str | None = None


class ColorCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    hex_code: str | None = Field(default=None, max_length=7)


class SeasonRead(ORMModel):
    id: int
    name: str


class SeasonCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)


class CollectionCreate(BaseModel):
    season_id: int
    name: str = Field(min_length=2, max_length=120)
    launch_year: int = Field(default=2026, ge=2000, le=2100)


class CollectionUpdate(BaseModel):
    season_id: int | None = None
    name: str | None = Field(default=None, min_length=2, max_length=120)
    launch_year: int | None = Field(default=None, ge=2000, le=2100)
    is_active: bool | None = None


class CollectionRead(ORMModel):
    id: int
    season_id: int
    name: str
    launch_year: int
    is_active: bool


class CatalogItemRead(ORMModel):
    id: int
    name: str
    description: str | None = None
    base_price: float
    min_price: float
    in_stock: bool
    is_ar_enabled: bool
    category: CategoryRead | None = None
    images: list["CatalogImageRead"] = []
    variants: list["CatalogVariantRead"] = []


class CatalogImageRead(ORMModel):
    id: int
    url: str
    is_primary: bool


class CatalogVariantRead(ORMModel):
    id: int
    sku: str
    price: float
    size_name: str
    color_name: str


class ArVariantRead(ORMModel):
    id: int
    sku: str
    size_name: str
    color_name: str


class ArConfigRead(ORMModel):
    garment_id: int
    garment_name: str
    is_ar_enabled: bool
    variants: list[ArVariantRead] = []


CatalogItemRead.model_rebuild()

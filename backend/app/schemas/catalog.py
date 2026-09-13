
from app.schemas.common import ORMModel


class CategoryRead(ORMModel):
    id: int
    name: str
    description: str | None = None
    is_active: bool


class CollectionRead(ORMModel):
    id: int
    season_id: int
    name: str
    launch_year: int


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


CatalogItemRead.model_rebuild()

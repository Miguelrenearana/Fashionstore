from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class PromotionBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=300)
    discount_percent: Decimal = Field(ge=0, le=100)
    start_at: datetime
    end_at: datetime


class PromotionCreate(PromotionBase):
    garment_ids: list[int] = Field(default_factory=list, min_length=1)


class PromotionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=300)
    discount_percent: Decimal | None = Field(default=None, ge=0, le=100)
    start_at: datetime | None = None
    end_at: datetime | None = None
    garment_ids: list[int] | None = None


class PromotionRead(ORMModel):
    id: int
    name: str
    description: str | None = None
    discount_percent: Decimal
    start_at: datetime
    end_at: datetime
    status: str
    created_at: datetime
    updated_at: datetime
    garment_ids: list[int] = []


class PromotionGarmentRead(ORMModel):
    id: int
    promotion_id: int
    garment_id: int
    garment_name: str


class PromotionWithGarmentsRead(PromotionRead):
    garments: list[PromotionGarmentRead] = []


class PromotionPageResponse(BaseModel):
    items: list[PromotionRead]
    total: int
    page: int
    size: int
    pages: int

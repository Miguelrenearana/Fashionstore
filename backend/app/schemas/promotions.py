from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from typing import Optional, List

from app.schemas.common import ORMModel


class PromotionBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: Optional[str] = Field(default=None, max_length=300)
    discount_percent: Decimal = Field(ge=0, le=100)
    start_at: datetime
    end_at: datetime


class PromotionCreate(PromotionBase):
    garment_ids: List[int] = Field(default_factory=list, min_length=1)


class PromotionUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    description: Optional[str] = Field(default=None, max_length=300)
    discount_percent: Optional[Decimal] = Field(default=None, ge=0, le=100)
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    garment_ids: Optional[List[int]] = None


class PromotionRead(ORMModel):
    id: int
    name: str
    description: Optional[str] = None
    discount_percent: Decimal
    start_at: datetime
    end_at: datetime
    status: str
    created_at: datetime
    updated_at: datetime
    garment_ids: List[int] = []


class PromotionGarmentRead(ORMModel):
    id: int
    promotion_id: int
    garment_id: int
    garment_name: str


class PromotionWithGarmentsRead(PromotionRead):
    garments: List[PromotionGarmentRead] = []


class PromotionPageResponse(BaseModel):
    items: List[PromotionRead]
    total: int
    page: int
    size: int
    pages: int
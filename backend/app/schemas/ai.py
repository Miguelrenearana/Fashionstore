from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Literal

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


# ============================================================
# CU-30: Recomendaciones
# ============================================================

class RecommendationItem(ORMModel):
    variant_id: int
    garment_name: str
    variant_sku: str
    size_name: str | None = None
    color_name: str | None = None
    price: float
    score: float
    garment_image_url: Optional[str] = None


class RecommendationResponse(ORMModel):
    items: List[RecommendationItem]
    source: Literal["similarity", "history", "trending"] = "similarity"


# ============================================================
# CU-31: Asistente IA (Chat)
# ============================================================

class AIChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class AIChatRequest(BaseModel):
    messages: List[AIChatMessage] = Field(min_length=1)
    context: Optional[str] = None  # Contexto adicional (catálogo, FAQ, etc.)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=500, ge=1, le=2000)


class AIChatResponse(BaseModel):
    message: str
    tokens_used: Optional[int] = None
    model: str
    finish_reason: str


# ============================================================
# CU-32: Generar consultas y reportes mediante IA (SQL Generation)
# ============================================================

class AIReportRequest(BaseModel):
    prompt: str = Field(min_length=5, max_length=2000)
    max_rows: int = Field(default=100, ge=1, le=1000)
    explain: bool = False  # Si True, devuelve el SQL generado también


class AIReportColumn(BaseModel):
    name: str
    type: str


class AIReportResponse(BaseModel):
    columns: List[AIReportColumn]
    rows: List[List[Optional[str]]]
    row_count: int
    generated_sql: Optional[str] = None
    execution_time_ms: float


# ============================================================
# Schemas adicionales para compatibilidad
# ============================================================

class RecommendationRead(ORMModel):
    id: int
    source_variant_id: int | None
    suggested_variant_id: int
    score: float
    variant_name: str | None = None
    variant_sku: str | None = None
    garment_id: int | None = None


class AIChatRequestLegacy(BaseModel):
    message: str
    context: Optional[str] = None


class AIChatResponseLegacy(BaseModel):
    response: str
    model: str
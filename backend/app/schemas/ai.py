from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

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
    garment_image_url: str | None = None


class RecommendationResponse(ORMModel):
    items: list[RecommendationItem]
    source: Literal["similarity", "history", "trending"] = "similarity"


# ============================================================
# CU-31: Asistente IA (Chat)
# ============================================================

class AIChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class AIChatRequest(BaseModel):
    messages: list[AIChatMessage] = Field(min_length=1)
    context: str | None = None  # Contexto adicional (catálogo, FAQ, etc.)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=500, ge=1, le=2000)

    @model_validator(mode="before")
    @classmethod
    def _accept_legacy_single_message(cls, data: Any) -> Any:
        """
        Acepta tambien el contrato en singular que usan los clientes
        (CU-31): {"message": "...", "history": [{"role","content"}]}.
        Se normaliza a `messages` para no duplicar el esquema.
        """
        if not isinstance(data, dict):
            return data
        if "messages" in data:
            return data

        message = data.get("message")
        if not isinstance(message, str) or not message.strip():
            raise ValueError("Debe enviar 'messages' o 'message' con la consulta del cliente.")

        messages: list[dict] = []
        for entry in data.get("history") or []:
            if isinstance(entry, dict) and entry.get("role") and entry.get("content") is not None:
                messages.append({"role": entry["role"], "content": entry["content"]})
        messages.append({"role": "user", "content": message})

        normalized = {k: v for k, v in data.items() if k not in {"message", "history"}}
        normalized["messages"] = messages
        return normalized

    @property
    def last_user_message(self) -> str:
        for msg in reversed(self.messages):
            if msg.role == "user":
                return msg.content
        return self.messages[-1].content

    @property
    def history(self) -> list[dict]:
        return [{"role": m.role, "content": m.content} for m in self.messages[:-1]]


class AIChatResponse(BaseModel):
    message: str
    tokens_used: int | None = None
    model: str
    finish_reason: str = "stop"


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
    columns: list[AIReportColumn]
    rows: list[list[str | None]]
    row_count: int
    generated_sql: str | None = None
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
    context: str | None = None


class AIChatResponseLegacy(BaseModel):
    response: str
    model: str

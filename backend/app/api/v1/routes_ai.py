from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.dependencies import CurrentUser, DbSession
from app.core.exceptions import NotFoundError
from app.models.catalog import GarmentVariant
from app.models.user import Client
from app.schemas.ai import (
    AIChatRequest,
    AIChatResponse,
    AIReportRequest,
    AIReportResponse,
)
from app.services.ai_service import ai_service

router = APIRouter(prefix="/ai", tags=["ai"])


def _client_id(db, user) -> int:
    client = db.query(Client).filter(Client.user_id == user.id).first()
    if not client:
        raise NotFoundError("Cliente no encontrado")
    return client.id


# ============================================================
# CU-30: Recomendaciones
# ============================================================

@router.get("/recommendations", response_model=list[dict])
def get_recommendations(
    db: DbSession,
    current: CurrentUser,
    source_variant_id: int | None = Query(None),
    limit: int = Query(10, ge=1, le=50),
    source: str = Query("similarity", pattern="^(similarity|history|trending)$"),
):
    """
    Obtener recomendaciones personalizadas.
    - source=similarity: productos similares a source_variant_id
    - source=history: basado en historial de navegación del cliente
    - source=trending: productos tendencia
    """
    client_id = _client_id(db, current)

    if source == "trending":
        results = ai_service.get_trending_products(db, limit=limit)
        return results

    if source == "history":
        recs = ai_service.recommend_for_client(db, client_id=_client_id(db, current), source_variant_id=source_variant_id, limit=limit)
        # Transformar a formato de respuesta
        results = []
        for rec in recs:
            variant = db.query(GarmentVariant).get(rec.suggested_variant_id)
            if variant and variant.garment:
                results.append({
                    "variant_id": variant.id,
                    "garment_name": variant.garment.name,
                    "variant_sku": variant.sku,
                    "size_name": variant.size.name if variant.size else None,
                    "color_name": variant.color.name if variant.color else None,
                    "price": float(variant.price) if variant.price else 0,
                    "score": float(rec.score),
                })
        return results

    # similarity (default)
    results = ai_service.get_recommendations_by_variant(db, source_variant_id, limit)
    return results


@router.get("/recommendations/trending", response_model=list[dict])
def get_trending_products(
    db: DbSession,
    limit: int = Query(10, ge=1, le=50),
):
    """Productos tendencia (más vistos/comprados)."""
    return ai_service.get_trending_products(db, limit)


@router.get("/recommendations/by-variant/{variant_id}", response_model=list[dict])
def get_recommendations_by_variant(
    variant_id: int,
    db: DbSession,
    limit: int = Query(10, ge=1, le=50),
):
    """Productos similares a una variante específica."""
    return ai_service.get_recommendations_by_variant(db, variant_id, limit)


@router.post("/view/{variant_id}")
def log_view(variant_id: int, db: DbSession, current: CurrentUser):
    """Registrar vista de producto para recomendaciones basadas en historial."""
    client_id = _client_id(db, current)
    ai_service.log_view(db, client_id, variant_id)
    return {"ok": True}


# ============================================================
# CU-31: Asistente IA (Chat)
# ============================================================

class AIChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant|system)$")
    content: str


class AIChatRequest(BaseModel):
    message: str
    context: str | None = None
    history: list[dict] = []
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=500, ge=1, le=2000)


class AIChatResponse(BaseModel):
    message: str
    model: str
    tokens_used: int | None = None


@router.post("/chat", response_model=dict)
def ai_chat(
    request: AIChatRequest,
    db: DbSession,
    current: CurrentUser,
):
    """Chat con asistente IA (Ollama local)."""
    try:
        result = ai_service.chat_with_context(
            message=request.message,
            context=request.context,
            history=request.history,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        return {
            "message": result.get("message", ""),
            "model": result.get("model", "unknown"),
            "tokens_used": result.get("tokens", 0),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en chat IA: {str(e)}")


# ============================================================
# CU-32: Generar consultas y reportes mediante IA (SQL Generation)
# ============================================================

class AIReportRequest(BaseModel):
    prompt: str = Field(min_length=5, max_length=2000)
    max_rows: int = Field(default=100, ge=1, le=1000)
    explain: bool = False


class AIReportResponse(BaseModel):
    columns: list[str]
    rows: list[list[str | None]]
    row_count: int
    generated_sql: str | None = None
    execution_time_ms: float


@router.post("/reports/generate", response_model=dict)
def generate_ai_report(
    request: AIReportRequest,
    db: DbSession,
    current: CurrentUser,
):
    """
    Generar reporte SQL desde lenguaje natural.
    Solo ADMIN puede usar este endpoint.
    """
    # Verificar rol ADMIN
    if "ADMIN" not in [r.name for r in current.roles]:
        raise HTTPException(status_code=403, detail="Solo administradores pueden generar reportes IA")

    try:
        result = ai_service.generate_ai_report(request.prompt, request.max_rows)
        return {
            "columns": result.get("columns", []),
            "rows": result.get("rows", []),
            "row_count": result.get("row_count", 0),
            "generated_sql": result.get("generated_sql"),
            "execution_time_ms": result.get("execution_time_ms", 0),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando reporte: {str(e)}")


@router.post("/reports/explain")
def explain_sql(
    prompt: str,
    db: DbSession,
    current: CurrentUser,
):
    """Generar y explicar SQL sin ejecutar."""
    if "ADMIN" not in [r.name for r in current.roles]:
        raise HTTPException(status_code=403, detail="Solo administradores")

    try:
        result = ai_service.generate_sql_query(prompt)
        return {
            "sql": result.get("sql"),
            "explanation": result.get("explanation", ""),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando SQL: {str(e)}")


# ============================================================
# Helpers
# ============================================================

def _client_id(db, user) -> int:
    client = db.query(Client).filter(Client.user_id == user.id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return client.id

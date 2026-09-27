from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import CurrentUser, DbSession
from app.core.exceptions import NotFoundError
from app.models.catalog import GarmentVariant
from app.models.user import Client, User
from app.schemas.ai import (
    AIChatRequest,
    AIChatResponse,
    AIReportRequest,
    AIReportResponse,
    RecommendationItem,
)
from app.services.ai_service import ai_service

router = APIRouter(prefix="/ai", tags=["ai"])


def _client_id(db: Session, user: User) -> int:
    client = db.query(Client).filter(Client.user_id == user.id).first()
    if not client:
        raise NotFoundError("Cliente no encontrado")
    return client.id


def _require_admin(current: User) -> None:
    """CU-32: solo A2 Administrador."""
    if "ADMIN" not in [r.name for r in current.roles]:
        raise HTTPException(status_code=403, detail="Solo administradores pueden generar reportes IA")


def _first_image(variant: GarmentVariant) -> str | None:
    """CU-30: imagen de la prenda para la tarjeta de recomendación."""
    images = getattr(variant.garment, "images", None) if variant.garment else None
    if images:
        return images[0].url
    return None


# ============================================================
# CU-30: Recomendaciones
# ============================================================

@router.get("/recommendations", response_model=list[RecommendationItem])
def get_recommendations(
    db: DbSession,
    current: CurrentUser,
    source_variant_id: int | None = Query(None),
    limit: int = Query(10, ge=1, le=50),
    source: str = Query("similarity", pattern="^(similarity|history|trending)$"),
):
    """
    CU-30: recomendar productos considerando preferencias, historial,
    temporada, categoría, talla y disponibilidad.
    - source=similarity: productos similares a source_variant_id
    - source=history: basado en historial de navegación del cliente
    - source=trending: productos tendencia
    """
    client_id = _client_id(db, current)

    if source == "trending":
        results = ai_service.get_trending_products(db, limit=limit)
    elif source == "history":
        recs = ai_service.recommend_for_client(
            db, client_id=client_id, source_variant_id=source_variant_id, limit=limit
        )
        results = []
        for rec in recs:
            variant = db.get(GarmentVariant, rec.suggested_variant_id)
            if variant and variant.garment:
                results.append({
                    "variant_id": variant.id,
                    "garment_name": variant.garment.name,
                    "variant_sku": variant.sku,
                    "size_name": variant.size.name if variant.size else None,
                    "color_name": variant.color.name if variant.color else None,
                    "price": float(variant.price) if variant.price else 0,
                    "score": float(rec.score),
                    "garment_image_url": _first_image(variant),
                })
    else:  # similarity (default)
        results = ai_service.get_recommendations_by_variant(db, source_variant_id, limit)

    return results


@router.get("/recommendations/trending", response_model=list[RecommendationItem])
def get_trending_products(
    db: DbSession,
    limit: int = Query(10, ge=1, le=50),
):
    """Productos tendencia (más vistos/comprados)."""
    results = ai_service.get_trending_products(db, limit)
    for item in results:
        variant = db.get(GarmentVariant, item["variant_id"])
        if variant:
            item["garment_image_url"] = _first_image(variant)
    return results


@router.get("/recommendations/by-variant/{variant_id}", response_model=list[RecommendationItem])
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
# CU-31: Asistir al cliente mediante IA (Chat con AS3)
# ============================================================

@router.post("/chat", response_model=AIChatResponse)
def ai_chat(
    request: AIChatRequest,
    db: DbSession,
    current: CurrentUser,
):
    """
    CU-31: el cliente introduce una consulta, el sistema la envía al
    servicio de IA (AS3) y presenta la respuesta.
    Acepta el contrato canónico `messages` y el shorthand `message`+`history`.
    """
    try:
        result = ai_service.chat_with_context(
            message=request.last_user_message,
            context=request.context,
            history=request.history,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
    except Exception as e:
        # EXCEPCION CU-31: "Servicio IA no disponible" / "Error de comunicación"
        raise HTTPException(status_code=503, detail=f"Asistencia inteligente no disponible: {e}") from e

    return AIChatResponse(
        message=result.get("message", ""),
        model=result.get("model", "unknown"),
        tokens_used=result.get("tokens", 0),
        finish_reason="stop" if result.get("done", True) else "length",
    )


# ============================================================
# CU-32: Generar consultas y reportes mediante IA (NL -> SQL)
# ============================================================

@router.post("/reports/generate", response_model=AIReportResponse)
def generate_ai_report(
    request: AIReportRequest,
    db: DbSession,
    current: CurrentUser,
):
    """CU-32: generar y ejecutar un reporte a partir de lenguaje natural. Solo A2."""
    _require_admin(current)

    try:
        result = ai_service.execute_ai_report(request.prompt, request.max_rows)
    except Exception as e:
        # EXCEPCION CU-32: "Solicitud no comprendida" / "Error de procesamiento"
        raise HTTPException(status_code=400, detail=str(e)) from e

    return AIReportResponse(**result)


@router.post("/reports/explain")
def explain_sql(
    db: DbSession,
    current: CurrentUser,
    prompt: str = Query(..., min_length=5, max_length=2000),
):
    """CU-32: generar y explicar el SQL sin ejecutarlo. Solo A2."""
    _require_admin(current)

    try:
        result = ai_service.generate_sql_query(prompt)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {"sql": result.get("sql"), "explanation": result.get("explanation", "")}



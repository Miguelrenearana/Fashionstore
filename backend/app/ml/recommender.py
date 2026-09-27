from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import coalesce

from app.core.exceptions import NotFoundError
from app.ml.embeddings import EmbeddingService
from app.ml.vector_store import VectorStore
from app.models.analytics import BrowsingHistory
from app.models.catalog import Garment, GarmentVariant
from app.models.inventory import Inventory


class RecommenderService:
    def __init__(self, embeddings: EmbeddingService | None = None):
        self._embeddings = embeddings or EmbeddingService()

    def embed_product(self, variant: GarmentVariant, garment: Garment | None = None) -> list[float]:
        garment = garment or variant.garment
        text = EmbeddingService.product_text(
            garment.name,
            garment.category.name if garment.category else None,
            garment.description,
        )
        return self._embeddings.encode(text).tolist()

    def get_recommendations(
        self, db: Session, source_variant_id: int | None, client_id: int | None, limit: int = 10
    ) -> list[tuple[int, float]]:
        query_text: str | None = None
        source_variant = None
        if source_variant_id:
            source_variant = db.get(GarmentVariant, source_variant_id)
            if not source_variant:
                raise NotFoundError("Source variant not found.")
            query_text = self._build_text(source_variant)
        elif client_id:
            history = (
                db.query(BrowsingHistory)
                .filter(BrowsingHistory.client_id == client_id)
                .order_by(BrowsingHistory.view_count.desc())
                .first()
            )
            if history:
                source_variant = db.get(GarmentVariant, history.variant_id)
                if source_variant:
                    query_text = self._build_text(source_variant)

        # El embedding se calcula con nombre/categoria/descripcion, asi que todas
        # las variantes de una misma prenda son identicas entre si (similitud
        # 1.0). Recomendar otra talla de la prenda que ya se esta viendo no aporta
        # nada, por lo que se excluye la prenda completa.
        exclude: list[int] | None = None
        if source_variant:
            exclude = [
                row[0]
                for row in db.query(GarmentVariant.id)
                .filter(GarmentVariant.garment_id == source_variant.garment_id)
                .all()
            ]
        if query_text:
            vector = self._embeddings.encode(query_text).tolist()
            # El ranking de pgvector es por variante, y dentro de una misma prenda
            # todas las variantes puntuan igual. Sin agrupar, el carrusel del movil
            # repetiria el mismo producto en varias tallas. Se piden mas candidatos
            # de los necesarios y se queda con uno por prenda, prefiriendo el que
            # tiene stock.
            candidates = VectorStore.recommend(vector, limit=limit * 4, exclude_ids=exclude)
            return self._one_variant_per_garment(db, candidates, limit)
        return []

    def _one_variant_per_garment(
        self, db: Session, candidates: list[tuple[int, float]], limit: int
    ) -> list[tuple[int, float]]:
        if not candidates:
            return []
        variant_ids = [vid for vid, _ in candidates]
        meta = {
            vid: (garment_id, available)
            for vid, garment_id, available in db.query(
                GarmentVariant.id,
                GarmentVariant.garment_id,
                coalesce(
                    func.sum(Inventory.quantity - Inventory.reserved_quantity), 0
                ).label("available"),
            )
            .outerjoin(Inventory, Inventory.variant_id == GarmentVariant.id)
            .filter(GarmentVariant.id.in_(variant_ids))
            .group_by(GarmentVariant.id, GarmentVariant.garment_id)
            .all()
        }

        seen: set[int] = set()
        result: list[tuple[int, float]] = []
        for variant_id, score in sorted(
            candidates, key=lambda c: -meta.get(c[0], (0, 0))[1]
        ):
            garment_id, _ = meta.get(variant_id, (None, 0))
            if garment_id is None or garment_id in seen:
                continue
            seen.add(garment_id)
            result.append((variant_id, score))
            if len(result) >= limit:
                break
        return result

    def _build_text(self, variant: GarmentVariant) -> str:
        garment = variant.garment
        return EmbeddingService.product_text(
            garment.name,
            garment.category.name if garment.category else None,
            garment.description,
        )

from app.core.config import settings
from app.core.database import SessionLocal
from app.ml.embeddings import EmbeddingService
from app.ml.vector_store import VectorStore
from app.models.catalog import Garment, GarmentVariant


def recompute_embeddings() -> int:
    """Backfill product_embeddings for all garment variants."""
    service = EmbeddingService()
    model_name = settings.recommendation_embedding_model
    db = SessionLocal()
    count = 0
    try:
        variants = db.query(GarmentVariant).all()
        batches = [
            variants[i : i + 64] for i in range(0, len(variants), 64)
        ]
        for batch in batches:
            garments = {
                g.id: g
                for g in db.query(Garment).filter(
                    Garment.id.in_([v.garment_id for v in batch])
                )
            }
            texts = []
            for v in batch:
                g = garments[v.garment_id]
                texts.append(
                    EmbeddingService.product_text(g.name, g.category.name if g.category else None, g.description)
                )
            vectors = service.encode_batch(texts)
            for v, vec in zip(batch, vectors, strict=False):
                VectorStore.save(v.id, vec.tolist(), model_name)
                count += 1
        VectorStore.create_index()
        db.commit()
        return count
    finally:
        db.close()

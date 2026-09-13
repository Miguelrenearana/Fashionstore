from sqlalchemy import text

from app.core.database import engine


class VectorStore:
    """pgvector operations for product embeddings (cosine similarity)."""

    DIMENSIONS = 384
    INDEX_QUERY = text(
        "SELECT indexname FROM pg_indexes WHERE tablename = 'product_embeddings'"
    )
    UPDATE_EMBEDDING = text("UPDATE product_embeddings SET embedding = :vector WHERE id = :id")
    UPSERT = text(
        """
        INSERT INTO product_embeddings (variant_id, model, embedding)
        VALUES (:variant_id, :model, :vector)
        ON CONFLICT (variant_id) DO UPDATE SET embedding = EXCLUDED.embedding, model = EXCLUDED.model
        """
    )

    @classmethod
    def save(cls, variant_id: int, vector: list[float], model: str) -> None:
        with engine.begin() as conn:
            conn.execute(cls.UPSERT, {"variant_id": variant_id, "model": model, "vector": vector})

    @classmethod
    def index_exists(cls) -> bool:
        with engine.connect() as conn:
            rows = conn.execute(cls.INDEX_QUERY).fetchall()
        names = {r[0] for r in rows}
        return "ix_product_embeddings_vector" in names or any(
            "embedding" in n for n in names
        )

    @classmethod
    def create_index(cls) -> None:
        stmt = text(
            "CREATE INDEX IF NOT EXISTS ix_product_embeddings_vector "
            "ON product_embeddings USING ivfflat (embedding vector_cosine_ops) "
            "WITH (lists = 100)"
        )
        with engine.begin() as conn:
            conn.execute(stmt)

    @classmethod
    def recommend(cls, vector: list[float], limit: int = 10, exclude_ids: list[int] | None = None) -> list[tuple[int, float]]:
        exclusions = ""
        params = {"vec": vector, "limit": limit}
        if exclude_ids:
            exclusions = "AND variant_id != ALL(:exclude_ids)"
            params["exclude_ids"] = exclude_ids
        query = text(
            "SELECT variant_id, 1 - (embedding <=> :vec) AS score "
            "FROM product_embeddings "
            f"WHERE embedding IS NOT NULL {exclusions} "
            "ORDER BY embedding <=> :vec "
            "LIMIT :limit"
        )
        with engine.connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [(int(r[0]), float(r[1])) for r in rows]

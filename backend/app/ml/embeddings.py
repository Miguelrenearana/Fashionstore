
import numpy as np

from app.core.config import settings


class EmbeddingService:
    """Thin wrapper over sentence-transformers with local cache."""

    _model = None

    def _load(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(settings.recommendation_embedding_model)
        return self._model

    def encode_batch(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.array([], dtype=np.float32)
        model = self._load()
        return model.encode(texts, normalize_embeddings=True).astype(np.float32)

    def encode(self, text: str) -> np.ndarray:
        return self.encode_batch([text])[0]

    @staticmethod
    def product_text(name: str, category: str | None, description: str | None) -> str:
        return f"{name} {category or ''} {description or ''}".strip()

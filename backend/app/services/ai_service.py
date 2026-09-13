from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.ml.recommender import RecommenderService
from app.models.analytics import BrowsingHistory, Recommendation


class AIService:
    def recommend_for_client(
        self, db: Session, client_id: int, source_variant_id: int | None, limit: int
    ) -> list[Recommendation]:
        recommender = RecommenderService()
        scored = recommender.get_recommendations(db, source_variant_id, client_id, limit)
        if not scored:
            return []
        stored: list[Recommendation] = []
        for variant_id, score in scored:
            rec = db.query(Recommendation).filter(
                Recommendation.suggested_variant_id == variant_id,
                Recommendation.client_id == client_id,
            ).first()
            if rec:
                rec.score = score
            else:
                rec = Recommendation(
                    client_id=client_id,
                    source_variant_id=source_variant_id,
                    suggested_variant_id=variant_id,
                    score=score,
                )
                db.add(rec)
            stored.append(rec)
        db.commit()
        return stored

    def log_view(self, db: Session, client_id: int, variant_id: int) -> None:
        entry = db.query(BrowsingHistory).filter(
            BrowsingHistory.client_id == client_id,
            BrowsingHistory.variant_id == variant_id,
        ).first()
        if entry:
            entry.view_count += 1
        else:
            db.add(BrowsingHistory(client_id=client_id, variant_id=variant_id, view_count=1))
        db.commit()

    def notify_variant_not_found(self, variant_id: int) -> None:
        if not variant_id:
            raise NotFoundError("Variant not found.")


ai_service = AIService()

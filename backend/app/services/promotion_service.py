from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.core.exceptions import NotFoundError, ValidationError
from app.models.analytics import Promotion, PromotionGarment, PromotionStatus
from app.models.catalog import Garment


class PromotionService:
    def create(self, db: Session, name: str, description: Optional[str],
               discount_percent: float, start_at: datetime, end_at: datetime,
               garment_ids: list[int]) -> dict:
        if not garment_ids:
            raise ValidationError("Debe asociar al menos una prenda a la promoción.")
        
        # Validar fechas
        if start_at >= end_at:
            raise ValidationError("La fecha de inicio debe ser anterior a la fecha de fin.")
        
        # Verificar que las prendas existan y estén activas
        garments = db.query(Garment).filter(
            Garment.id.in_(garment_ids),
            Garment.is_active == True
        ).all()
        if len(garments) != len(garment_ids):
            found_ids = {g.id for g in garments}
            missing = set(garment_ids) - found_ids
            raise NotFoundError(f"Prendas no encontradas o inactivas: {missing}")
        
        promotion = Promotion(
            name=name,
            description=description,
            discount_percent=discount_percent,
            start_at=start_at,
            end_at=end_at,
            status=PromotionStatus.ACTIVE,
        )
        db.add(promotion)
        db.flush()
        
        for garment in garments:
            promo_garment = PromotionGarment(
                promotion_id=promotion.id,
                garment_id=garment.id,
            )
            db.add(promo_garment)
        
        db.commit()
        db.refresh(promotion)
        
        return {
            "id": promotion.id,
            "name": promotion.name,
            "description": promotion.description,
            "discount_percent": promotion.discount_percent,
            "start_at": promotion.start_at,
            "end_at": promotion.end_at,
            "status": promotion.status,
            "created_at": promotion.created_at,
            "updated_at": promotion.updated_at,
            "garment_ids": [g.id for g in promotion.garments],
        }

    def update(self, db: Session, promotion_id: int, **kwargs) -> dict:
        promotion = db.query(Promotion).filter(Promotion.id == promotion_id).first()
        if not promotion:
            raise NotFoundError("Promoción no encontrada.")
        
        if "name" in kwargs and kwargs["name"] is not None:
            promotion.name = kwargs["name"]
        if "description" in kwargs and kwargs["description"] is not None:
            promotion.description = kwargs["description"]
        if "discount_percent" in kwargs and kwargs["discount_percent"] is not None:
            promotion.discount_percent = kwargs["discount_percent"]
        if "start_at" in kwargs and kwargs["start_at"] is not None:
            promotion.start_at = kwargs["start_at"]
        if "end_at" in kwargs and kwargs["end_at"] is not None:
            promotion.end_at = kwargs["end_at"]
        
        # Validar fechas si ambas están presentes
        if promotion.start_at >= promotion.end_at:
            raise ValidationError("La fecha de inicio debe ser anterior a la fecha de fin.")
        
        # Actualizar prendas si se proporciona garment_ids
        if "garment_ids" in kwargs and kwargs["garment_ids"] is not None:
            garment_ids = kwargs["garment_ids"]
            if not garment_ids:
                raise ValidationError("Debe asociar al menos una prenda a la promoción.")
            
            garments = db.query(Garment).filter(
                Garment.id.in_(garment_ids),
                Garment.is_active == True
            ).all()
            if len(garments) != len(garment_ids):
                found_ids = {g.id for g in garments}
                missing = set(garment_ids) - {g.id for g in garments}
                raise NotFoundError(f"Prendas no encontradas o inactivas: {missing}")
            
            # Eliminar asociaciones existentes
            db.query(PromotionGarment).filter(
                PromotionGarment.promotion_id == promotion.id
            ).delete()
            
            for garment in garments:
                promo_garment = PromotionGarment(
                    promotion_id=promotion.id,
                    garment_id=garment.id,
                )
                db.add(promo_garment)
        
        db.commit()
        db.refresh(promotion)
        
        return self._to_dict(promotion)

    def get(self, db: Session, promotion_id: int) -> dict:
        promotion = db.query(Promotion).options(
            joinedload(Promotion.garments)
        ).filter(Promotion.id == promotion_id).first()
        if not promotion:
            raise NotFoundError("Promoción no encontrada.")
        return self._to_dict(promotion)

    def list(self, db: Session, page: int = 1, size: int = 20,
             active_only: bool = False, search: str | None = None) -> tuple[list, int]:
        query = db.query(Promotion)
        
        if active_only:
            now = datetime.now(UTC)
            query = query.filter(
                Promotion.status == PromotionStatus.ACTIVE,
                Promotion.start_at <= datetime.now(UTC),
                Promotion.end_at >= datetime.now(UTC),
            )
        
        if search:
            like = f"%{search}%"
            query = query.filter(Promotion.name.ilike(like) | Promotion.description.ilike(like))
        
        total = query.count()
        items = query.order_by(Promotion.created_at.desc()).offset((page - 1) * size).limit(size).all()
        
        return [self._to_dict(p) for p in items], total

    def get_active(self, db: Session) -> list:
        now = datetime.now(UTC)
        promotions = db.query(Promotion).options(
            joinedload(Promotion.garments)
        ).filter(
            Promotion.status == PromotionStatus.ACTIVE,
            Promotion.start_at <= datetime.now(UTC),
            Promotion.end_at >= datetime.now(UTC),
        ).all()
        return [self._to_dict(p) for p in promotions]

    def delete(self, db: Session, promotion_id: int) -> None:
        promotion = db.query(Promotion).filter(Promotion.id == promotion_id).first()
        if not promotion:
            raise NotFoundError("Promoción no encontrada.")
        promotion.is_deleted = True
        db.commit()

    def _to_dict(self, promotion) -> dict:
        return {
            "id": promotion.id,
            "name": promotion.name,
            "description": promotion.description,
            "discount_percent": float(promotion.discount_percent),
            "start_at": promotion.start_at,
            "end_at": promotion.end_at,
            "status": promotion.status,
            "created_at": promotion.created_at,
            "updated_at": promotion.updated_at,
            "garment_ids": [g.id for g in promotion.garments] if promotion.garments else [],
        }


promotion_service = PromotionService()
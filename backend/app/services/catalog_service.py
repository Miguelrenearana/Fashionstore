from sqlalchemy.orm import Session, joinedload

from app.models.catalog import Garment


class CatalogService:
    def list_catalog(
        self,
        db: Session,
        page: int,
        size: int,
        category_id: int | None = None,
        search: str | None = None,
        branch_id: int | None = None,
    ):
        query = db.query(Garment).filter(Garment.is_active).options(
            joinedload(Garment.category),
            joinedload(Garment.images),
            joinedload(Garment.variations).joinedload("size"),
            joinedload(Garment.variations).joinedload("color"),
        )
        if category_id:
            query = query.filter(Garment.category_id == category_id)
        if search:
            like = f"%{search}%"
            query = query.filter(Garment.name.ilike(like) | Garment.description.ilike(like))
        total = query.count()
        items = query.order_by(Garment.id).offset((page - 1) * size).limit(size).all()
        return items, total

    def get(self, db: Session, garment_id: int) -> Garment:
        return db.get(Garment, garment_id)


catalog_service = CatalogService()

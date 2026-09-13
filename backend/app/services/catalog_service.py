from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import NotFoundError
from app.models.catalog import Category, Garment, GarmentVariant
from app.models.inventory import Inventory


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
            joinedload(Garment.variations).joinedload(GarmentVariant.size),
            joinedload(Garment.variations).joinedload(GarmentVariant.color),
            joinedload(Garment.variations).joinedload(GarmentVariant.inventory),
        )
        if category_id:
            query = query.filter(Garment.category_id == category_id)
        if search:
            like = f"%{search}%"
            query = query.filter(Garment.name.ilike(like) | Garment.description.ilike(like))
        if branch_id:
            query = (
                query.join(Garment.variations)
                .join(GarmentVariant.inventory)
                .filter(Inventory.branch_id == branch_id)
                .distinct()
            )
        total = query.count()
        items = query.order_by(Garment.id).offset((page - 1) * size).limit(size).all()
        return items, total

    def get(self, db: Session, garment_id: int) -> Garment:
        item = (
            db.query(Garment)
            .filter(Garment.id == garment_id, Garment.is_active)
            .options(
                joinedload(Garment.category),
                joinedload(Garment.images),
                joinedload(Garment.variations).joinedload(GarmentVariant.size),
                joinedload(Garment.variations).joinedload(GarmentVariant.color),
                joinedload(Garment.variations).joinedload(GarmentVariant.inventory),
            )
            .first()
        )
        if not item:
            raise NotFoundError("Garment not found.")
        return item

    def list_categories(self, db: Session) -> list[Category]:
        return db.query(Category).filter(Category.is_active).order_by(Category.name).all()


catalog_service = CatalogService()

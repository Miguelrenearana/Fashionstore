from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.catalog import Category, Color, Garment, GarmentVariant, Size
from app.schemas.product import GarmentCreate


class ProductService:
    def create(self, db: Session, payload: GarmentCreate) -> Garment:
        if not db.get(Category, payload.category_id):
            raise NotFoundError("Category not found.")
        if payload.collection_id and not db.get(Category, payload.collection_id):
            raise NotFoundError("Collection not found.")
        garment = Garment(
            category_id=payload.category_id,
            collection_id=payload.collection_id,
            name=payload.name,
            description=payload.description,
            base_price=payload.base_price,
            is_ar_enabled=payload.is_ar_enabled,
        )
        for v in payload.variants:
            variant = self._make_variant(db, garment, v)
            garment.variations.append(variant)
        try:
            db.add(garment)
            db.commit()
        except Exception as err:
            db.rollback()
            raise ConflictError("SKU already exists.") from err
        db.refresh(garment)
        return garment

    def get(self, db: Session, garment_id: int) -> Garment:
        garment = db.get(Garment, garment_id)
        if not garment:
            raise NotFoundError("Garment not found.")
        return garment

    def _make_variant(self, db: Session, garment: Garment, v) -> GarmentVariant:
        size = db.get(Size, v.size_id) if v.size_id else None
        color = db.get(Color, v.color_id) if v.color_id else None
        if not size and v.size_name:
            size = Size(name=v.size_name)
            db.add(size)
        if not color and v.color_name:
            color = Color(name=v.color_name)
            db.add(color)
        return GarmentVariant(
            garment=garment,
            size_id=size.id if size else None,
            color_id=color.id if color else None,
            sku=v.sku,
            price=v.price,
        )


product_service = ProductService()

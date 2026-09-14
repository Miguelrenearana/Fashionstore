from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.catalog import Category, Collection, Color, Season, Size


class CatalogConfigService:
    """Admin CRUD for catalog dimensions (CU-08, CU-09)."""

    def list_categories(self, db: Session) -> list[Category]:
        return db.query(Category).filter(Category.is_active).order_by(Category.name).all()

    def create_category(self, db: Session, payload) -> Category:
        item = Category(name=payload.name, description=payload.description)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def update_category(self, db: Session, item_id: int, payload) -> Category:
        item = db.query(Category).filter(Category.id == item_id).first()
        if not item:
            raise NotFoundError("Category not found.")
        data = payload.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(item, field, value)
        db.commit()
        db.refresh(item)
        return item

    def list_sizes(self, db: Session) -> list[Size]:
        return db.query(Size).order_by(Size.name).all()

    def create_size(self, db: Session, payload) -> Size:
        item = Size(name=payload.name)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def update_size(self, db: Session, item_id: int, payload) -> Size:
        item = db.query(Size).filter(Size.id == item_id).first()
        if not item:
            raise NotFoundError("Size not found.")
        data = payload.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(item, field, value)
        db.commit()
        db.refresh(item)
        return item

    def list_colors(self, db: Session) -> list[Color]:
        return db.query(Color).order_by(Color.name).all()

    def create_color(self, db: Session, payload) -> Color:
        item = Color(name=payload.name, hex_code=payload.hex_code)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def update_color(self, db: Session, item_id: int, payload) -> Color:
        item = db.query(Color).filter(Color.id == item_id).first()
        if not item:
            raise NotFoundError("Color not found.")
        data = payload.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(item, field, value)
        db.commit()
        db.refresh(item)
        return item

    def list_seasons(self, db: Session) -> list[Season]:
        return db.query(Season).order_by(Season.name).all()

    def create_season(self, db: Session, payload) -> Season:
        item = Season(name=payload.name)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def update_season(self, db: Session, item_id: int, payload) -> Season:
        item = db.query(Season).filter(Season.id == item_id).first()
        if not item:
            raise NotFoundError("Season not found.")
        data = payload.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(item, field, value)
        db.commit()
        db.refresh(item)
        return item

    def list_collections(self, db: Session) -> list[Collection]:
        return (
            db.query(Collection)
            .filter(Collection.is_active)
            .order_by(Collection.launch_year.desc())
            .all()
        )

    def create_collection(self, db: Session, payload) -> Collection:
        item = Collection(
            season_id=payload.season_id,
            name=payload.name,
            launch_year=payload.launch_year,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def update_collection(self, db: Session, item_id: int, payload) -> Collection:
        item = db.query(Collection).filter(Collection.id == item_id).first()
        if not item:
            raise NotFoundError("Collection not found.")
        data = payload.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(item, field, value)
        db.commit()
        db.refresh(item)
        return item


catalog_config_service = CatalogConfigService()

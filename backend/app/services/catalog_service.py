from sqlalchemy import and_, case, func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.exceptions import NotFoundError
from app.models.catalog import Category, Color, Garment, GarmentVariant, Size
from app.models.inventory import Inventory


class CatalogService:
    def _apply_stock(self, db: Session, garments: list[Garment], branch_id: int | None) -> None:
        """Resuelve stock/available de cada variante en una sola consulta (CU-14).

        Evita el N+1 sobre Inventory y respeta la sucursal seleccionada.
        """
        variant_ids = [v.id for g in garments for v in g.variations]
        if not variant_ids:
            return

        # Clamp por fila antes de sumar para que una fila sobre-reservada
        # no arrastre el total del grupo a negativo.
        free = Inventory.quantity - Inventory.reserved_quantity
        free = case((free < 0, 0), else_=free)

        query = (
            db.query(
                Inventory.variant_id,
                func.coalesce(func.sum(Inventory.quantity), 0).label("stock"),
                func.coalesce(func.sum(free), 0).label("available"),
            )
            .filter(Inventory.variant_id.in_(variant_ids))
        )
        if branch_id is not None:
            query = query.filter(Inventory.branch_id == branch_id)
        rows = query.group_by(Inventory.variant_id).all()

        by_variant = {vid: (int(stock), int(avail)) for vid, stock, avail in rows}
        for garment in garments:
            for variant in garment.variations:
                stock, avail = by_variant.get(variant.id, (0, 0))
                variant.set_stock(stock, avail)

    def list_catalog(
        self,
        db: Session,
        page: int,
        size: int,
        category_id: int | None = None,
        search: str | None = None,
        branch_id: int | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        sizes: list[str] | None = None,
        colors: list[str] | None = None,
        in_stock: bool = False,
        sort_by: str | None = None,
    ):
        query = db.query(Garment).filter(Garment.is_active).options(
            joinedload(Garment.category),
            selectinload(Garment.images),
            selectinload(Garment.variations).joinedload(GarmentVariant.size),
            selectinload(Garment.variations).joinedload(GarmentVariant.color),
            selectinload(Garment.variations).selectinload(GarmentVariant.inventory),
        )
        if category_id:
            query = query.filter(Garment.category_id == category_id)
        if search:
            like = f"%{search}%"
            query = query.filter(Garment.name.ilike(like) | Garment.description.ilike(like))
        if min_price is not None:
            query = query.filter(Garment.variations.any(GarmentVariant.price >= min_price))
        if max_price is not None:
            query = query.filter(Garment.variations.any(GarmentVariant.price <= max_price))
        if sizes or colors:
            # talla y color deben cumplirse en la MISMA variante; si se
            # filtraran por separado, una prenda entraria con talla M de un
            # color y color Negro de otra talla.
            criteria = []
            if sizes:
                criteria.append(
                    GarmentVariant.size_id.in_(db.query(Size.id).filter(Size.name.in_(sizes)))
                )
            if colors:
                criteria.append(
                    GarmentVariant.color_id.in_(db.query(Color.id).filter(Color.name.in_(colors)))
                )
            query = query.filter(Garment.variations.any(and_(*criteria)))
        if branch_id is not None or in_stock:
            # CU-14: solo prendas con existencias disponibles.
            query = query.filter(
                Garment.variations.any(
                    GarmentVariant.inventory.any(
                        Inventory.quantity > Inventory.reserved_quantity,
                        **({"branch_id": branch_id} if branch_id is not None else {}),
                    )
                )
            )

        # Se ordena por el precio de la variante mas barata, que es el que
        # muestra el catalogo; ordenar por base_price daria una lista que
        # parece desordenada para el usuario.
        cheapest = (
            select(func.min(GarmentVariant.price))
            .where(GarmentVariant.garment_id == Garment.id)
            .correlate(Garment)
            .scalar_subquery()
        )
        order = {
            "price_asc": cheapest.asc(),
            "price_desc": cheapest.desc(),
            "name_asc": Garment.name.asc(),
            "name_desc": Garment.name.desc(),
        }.get(sort_by or "", Garment.id)

        total = query.count()
        items = query.order_by(order, Garment.id).offset((page - 1) * size).limit(size).all()
        self._apply_stock(db, items, branch_id)
        return items, total

    def get(self, db: Session, garment_id: int, branch_id: int | None = None) -> Garment:
        item = (
            db.query(Garment)
            .filter(Garment.id == garment_id, Garment.is_active)
            .options(
                joinedload(Garment.category),
                selectinload(Garment.images),
                selectinload(Garment.variations).joinedload(GarmentVariant.size),
                selectinload(Garment.variations).joinedload(GarmentVariant.color),
                selectinload(Garment.variations)
                .selectinload(GarmentVariant.inventory)
                .joinedload(Inventory.branch),
            )
            .first()
        )
        if not item:
            raise NotFoundError("Garment not found.")
        self._apply_stock(db, [item], branch_id)
        return item

    def list_categories(self, db: Session) -> list[Category]:
        return db.query(Category).filter(Category.is_active).order_by(Category.name).all()

    def get_ar_config(self, db: Session, garment_id: int) -> Garment:
        item = (
            db.query(Garment)
            .filter(Garment.id == garment_id, Garment.is_active)
            .options(
                joinedload(Garment.variations).joinedload(GarmentVariant.size),
                joinedload(Garment.variations).joinedload(GarmentVariant.color),
            )
            .first()
        )
        if not item:
            raise NotFoundError("Garment not found.")
        return item


catalog_service = CatalogService()

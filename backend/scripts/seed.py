import secrets
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine
from app.core.security import hash_password
from app.models.analytics import (
    AuditLog,
    BrowsingHistory,
    Notification,
    Promotion,
    PromotionStatus,
)
from app.models.cart import Cart, CartDetail
from app.models.catalog import (
    Category,
    Collection,
    Color,
    Garment,
    GarmentImage,
    GarmentVariant,
    Season,
    Size,
)
from app.models.inventory import Inventory
from app.models.movement import (
    InventoryMovement,
    InventoryMovementType,
    Reception,
    ReceptionDetail,
)
from app.models.reservation import (
    Reservation,
    ReservationDetail,
    ReservationHistory,
    ReservationStatus,
)
from app.models.sales import (
    Payment,
    Receipt,
    Sale,
    SaleDetail,
    SalePaymentStatus,
    SaleStatus,
)
from app.models.user import Branch, City, Client, Employee, Role, Supplier, User

# Credenciales demo (NUNCA usar en producción).
# `sonclargod@gmail.com` es el cliente demo con email REAL (recibe correo real via SMTP).
DEMO_PASSWORDS = {
    "admin@fashionstore.dev": "Admin123!",
    "manager@fashionstore.dev": "Manager123!",
    "cashier@fashionstore.dev": "Cashier123!",
    "client@fashionstore.dev": "Client123!",
    "sonclargod@gmail.com": "Client123!",
    "supplier@fashionstore.dev": "Supplier123!",
}

REAL_CLIENT_EMAIL = "sonclargod@gmail.com"


def _ensure_user(db: Session, email: str, password: str, role_name: str) -> User:
    user = db.query(User).filter(User.email == email.lower()).first()
    if not user:
        user = User(email=email.lower(), password_hash=hash_password(password))
        db.add(user)
        db.flush()
    role = db.query(Role).filter(Role.name == role_name).first()
    if role and role not in user.roles:
        user.roles.append(role)
    return user


def _ensure_size(db: Session, name: str) -> Size:
    size = db.query(Size).filter(Size.name == name).first()
    if not size:
        size = Size(name=name)
        db.add(size)
        db.flush()
    return size


def _ensure_color(db: Session, name: str, hex_code: str) -> Color:
    color = db.query(Color).filter(Color.name == name).first()
    if not color:
        color = Color(name=name, hex_code=hex_code)
        db.add(color)
        db.flush()
    return color


def _ensure_category(db: Session, name: str, description: str) -> Category:
    category = db.query(Category).filter(Category.name == name).first()
    if not category:
        category = Category(name=name, description=description)
        db.add(category)
        db.flush()
    return category


def _ensure_garment(
    db: Session,
    category: Category,
    collection: Collection,
    name: str,
    description: str,
    base_price: float,
    is_ar_enabled: bool = False,
) -> Garment:
    garment = db.query(Garment).filter(Garment.name == name).first()
    if not garment:
        garment = Garment(
            category_id=category.id,
            collection_id=collection.id,
            name=name,
            description=description,
            base_price=base_price,
            is_ar_enabled=is_ar_enabled,
        )
        db.add(garment)
        db.flush()
        db.add(GarmentImage(
            garment_id=garment.id,
            url=f"https://fashionstore-sonclar.vercel.app/assets/garments/{name.lower().replace(' ', '-')}.png",
            is_primary=True,
        ))
        db.flush()
    return garment


def _ensure_variant(
    db: Session,
    garment: Garment,
    size: Size,
    color: Color,
    sku_prefix: str,
    price: float,
) -> GarmentVariant:
    variant = db.query(GarmentVariant).filter(
        GarmentVariant.garment_id == garment.id,
        GarmentVariant.size_id == size.id,
        GarmentVariant.color_id == color.id,
    ).first()
    if not variant:
        sku = f"{sku_prefix}-{size.name.upper()}-{color.name.upper()[:2]}-{secrets.token_hex(3).upper()}"
        variant = GarmentVariant(
            garment_id=garment.id,
            size_id=size.id,
            color_id=color.id,
            sku=sku,
            price=price,
        )
        db.add(variant)
        db.flush()
    return variant


def _ensure_inventory(db: Session, branch: Branch, variant: GarmentVariant, quantity: int) -> None:
    exists = db.query(Inventory).filter(
        Inventory.branch_id == branch.id,
        Inventory.variant_id == variant.id,
    ).first()
    if not exists:
        db.add(Inventory(branch_id=branch.id, variant_id=variant.id, quantity=quantity))
        db.flush()


def _ensure_promotion(
    db: Session,
    name: str,
    description: str,
    discount_percent: float,
    start_at: datetime,
    end_at: datetime,
) -> Promotion:
    promotion = db.query(Promotion).filter(Promotion.name == name).first()
    if not promotion:
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
    return promotion


def _make_paid_sale(
    db: Session,
    invoice_prefix: str,
    client: Client | None,
    branch: Branch,
    employee: Employee | None,
    items: list[tuple[GarmentVariant, int]],
    paid_at: datetime,
    payment_method: str = "QR",
    total: Decimal | None = None,
) -> Sale:
    """Crear una venta PAID con su detalle, pago completado y comprobante."""
    sale = Sale(
        invoice_number=f"FAC-{invoice_prefix}-{secrets.token_hex(3).upper()}",
        client_id=client.id if client else None,
        branch_id=branch.id,
        employee_id=employee.id if employee else None,
        total_amount=total or Decimal("0"),
        payment_method=payment_method,
        status=SaleStatus.PAID,
        paid_at=paid_at,
    )
    db.add(sale)
    db.flush()
    subtotal = Decimal("0")
    for variant, qty in items:
        subtotal += variant.price * qty
        db.add(SaleDetail(
            sale_id=sale.id,
            variant_id=variant.id,
            quantity=qty,
            unit_price=variant.price,
        ))
    sale.total_amount = total or subtotal
    db.add(Payment(
        sale_id=sale.id,
        gateway_reference=f"PAY-{secrets.token_hex(6).upper()}",
        amount=sale.total_amount,
        currency="BOB",
        method=payment_method,
        status=SalePaymentStatus.COMPLETED,
        qr_verified_at=paid_at,
        qr_manually_marked_paid=True,
    ))
    db.add(Receipt(
        sale_id=sale.id,
        type="invoice",
        rnc_or_cuf=f"78000001-1-26-{secrets.token_hex(4).upper()}",
        document_url=None,
    ))
    db.flush()
    return sale


def run() -> None:
    db = SessionLocal()

    roles = ["ADMIN", "MANAGER", "CASHIER", "CLIENT", "SUPPLIER"]
    for name in roles:
        if not db.query(Role).filter(Role.name == name).first():
            db.add(Role(name=name))
    db.commit()

    la_paz = City(name="La Paz", state="La Paz")
    santa_cruz = City(name="Santa Cruz", state="Santa Cruz")
    if not db.query(City).filter(City.name == "La Paz").first():
        db.add_all([la_paz, santa_cruz])
    db.commit()

    branch_lp = db.query(Branch).filter(Branch.name == "Sucursal Sopocachi").first()
    if not branch_lp:
        branch_lp = Branch(city_id=la_paz.id, name="Sucursal Sopocachi", address="Av. 6 de Agosto 1234")
        db.add(branch_lp)
        db.flush()
    branch_sc = db.query(Branch).filter(Branch.name == "Sucursal Equipetrol").first()
    if not branch_sc:
        branch_sc = Branch(city_id=santa_cruz.id, name="Sucursal Equipetrol", address="Av. San Martin 3456")
        db.add(branch_sc)
        db.flush()
    db.commit()

    # ---- Usuarios demo ----
    admin_user = _ensure_user(db, "admin@fashionstore.dev", DEMO_PASSWORDS["admin@fashionstore.dev"], "ADMIN")
    manager_user = _ensure_user(db, "manager@fashionstore.dev", DEMO_PASSWORDS["manager@fashionstore.dev"], "MANAGER")
    cashier_user = _ensure_user(db, "cashier@fashionstore.dev", DEMO_PASSWORDS["cashier@fashionstore.dev"], "CASHIER")
    demo_client_user = _ensure_user(db, "client@fashionstore.dev", DEMO_PASSWORDS["client@fashionstore.dev"], "CLIENT")
    real_client_user = _ensure_user(db, REAL_CLIENT_EMAIL, DEMO_PASSWORDS[REAL_CLIENT_EMAIL], "CLIENT")
    supplier_user = _ensure_user(db, "supplier@fashionstore.dev", DEMO_PASSWORDS["supplier@fashionstore.dev"], "SUPPLIER")
    db.commit()

    manager_employee = db.query(Employee).filter(Employee.user_id == manager_user.id).first()
    if not manager_employee:
        manager_employee = Employee(
            user_id=manager_user.id,
            branch_id=branch_lp.id,
            first_name="Gerente",
            last_name="Demo",
            hire_date=date(2025, 1, 10),
        )
        db.add(manager_employee)
        db.flush()
    cashier_employee = db.query(Employee).filter(Employee.user_id == cashier_user.id).first()
    if not cashier_employee:
        cashier_employee = Employee(
            user_id=cashier_user.id,
            branch_id=branch_lp.id,
            first_name="Cajero",
            last_name="Demo",
            hire_date=date(2025, 3, 15),
        )
        db.add(cashier_employee)
        db.flush()
    demo_client = db.query(Client).filter(Client.user_id == demo_client_user.id).first()
    if not demo_client:
        demo_client = Client(
            user_id=demo_client_user.id,
            first_name="Cliente",
            last_name="Demo",
            birth_date=date(1995, 5, 20),
            points=120,
        )
        db.add(demo_client)
        db.flush()
    real_client = db.query(Client).filter(Client.user_id == real_client_user.id).first()
    if not real_client:
        real_client = Client(
            user_id=real_client_user.id,
            first_name="Cliente",
            last_name="Real",
            birth_date=date(1993, 3, 10),
            points=340,
        )
        db.add(real_client)
        db.flush()
    supplier = db.query(Supplier).filter(Supplier.company_name == "Textiles Andinos SRL").first()
    if not supplier:
        supplier = Supplier(
            company_name="Textiles Andinos SRL",
            contact_name="Proveedor Demo",
            email=supplier_user.email,
            address="Zona Central, La Paz",
        )
        db.add(supplier)
        db.flush()
    db.commit()

    # ---- Catálogo ----
    season_ow = db.query(Season).filter(Season.name == "Otoño/Invierno 2026").first()
    if not season_ow:
        season_ow = Season(name="Otoño/Invierno 2026")
        db.add(season_ow)
        db.flush()
    season_pv = db.query(Season).filter(Season.name == "Primavera/Verano 2027").first()
    if not season_pv:
        season_pv = Season(name="Primavera/Verano 2027")
        db.add(season_pv)
        db.flush()
    collection_urbana = db.query(Collection).filter(Collection.name == "Colección Urbana").first()
    if not collection_urbana:
        collection_urbana = Collection(season_id=season_ow.id, name="Colección Urbana", launch_year=2026)
        db.add(collection_urbana)
        db.flush()
    collection_floral = db.query(Collection).filter(Collection.name == "Colección Floral").first()
    if not collection_floral:
        collection_floral = Collection(season_id=season_pv.id, name="Colección Floral", launch_year=2027)
        db.add(collection_floral)
        db.flush()

    cat_camisas = _ensure_category(db, "Camisas", "Prendas formales y casuales")
    cat_poleras = _ensure_category(db, "Poleras", "Hoodies y buzos para el día a día")
    cat_pantalones = _ensure_category(db, "Pantalones", "Todas las siluetas y cortes")
    cat_vestidos = _ensure_category(db, "Vestidos", "Cocktail, casual y largo")
    cat_chaquetas = _ensure_category(db, "Chaquetas", "Abrigos y casacas")
    db.commit()

    sizes = {
        "S": _ensure_size(db, "S"),
        "M": _ensure_size(db, "M"),
        "L": _ensure_size(db, "L"),
        "XL": _ensure_size(db, "XL"),
    }
    colors = {
        "Negro": _ensure_color(db, "Negro", "#000000"),
        "Blanco": _ensure_color(db, "Blanco", "#FFFFFF"),
        "Azul": _ensure_color(db, "Azul", "#1E3A5F"),
        "Rojo": _ensure_color(db, "Rojo", "#C0392B"),
        "Beige": _ensure_color(db, "Beige", "#D7C4A3"),
        "Verde": _ensure_color(db, "Verde", "#2E7D32"),
    }
    db.commit()

    garments = [
        # (nombre, categoría, colección, descripción, precio, AR)
        ("Camisa Oxford Básica", cat_camisas, collection_urbana, "Camisa de algodón, corte regular.", 180.0, True),
        ("Camisa Slim Rayas", cat_camisas, collection_urbana, "Camisa slim con rayas sutiles.", 220.0, False),
        ("Hoodie Urban Core", cat_poleras, collection_urbana, "Hoodie de algodón grueso con capucha.", 260.0, True),
        ("Buzo Classic", cat_poleras, collection_urbana, "Buzo clásico con bolsillo canguro.", 240.0, False),
        ("Pantalón Chino Slim", cat_pantalones, collection_urbana, "Chino slim para todas las ocasiones.", 200.0, False),
        ("Jeans Skinny", cat_pantalones, collection_urbana, "Denim elástico corte skinny.", 245.0, False),
        ("Vestido Casual", cat_vestidos, collection_floral, "Vestido casual de algodón.", 290.0, True),
        ("Vestido Largo", cat_vestidos, collection_floral, "Vestido largo estilo bohemio.", 350.0, True),
        ("Chaqueta Denim", cat_chaquetas, collection_urbana, "Casaca de jean clásica.", 320.0, True),
        ("Rompevientos Ligero", cat_chaquetas, collection_urbana, "Chaqueta rompevientos impermeable.", 310.0, False),
        ("Blusa Seda Floral", cat_camisas, collection_floral, "Blusa de seda con estampado floral.", 210.0, True),
        ("Camiseta Básica Algodón", cat_poleras, collection_floral, "Camiseta sin estampado, algodón 100%.", 120.0, False),
    ]

    all_variants: list[GarmentVariant] = []
    first_garment = None
    combos = [("S", "Negro"), ("M", "Blanco"), ("L", "Azul"), ("XL", "Rojo")]
    for idx, (name, cat, col, desc, price, is_ar) in enumerate(garments):
        g = _ensure_garment(db, cat, col, name, desc, price, is_ar)
        first_garment = first_garment or g
        sku_prefix = "".join(ch for ch in name.upper().split()[0] if ch.isalnum())
        # Variantes: 2-4 combinaciones talla/color por prenda
        n_variants = 2 if idx % 4 else 4
        for sz, col_name in combos[:n_variants]:
            size = sizes[sz]
            color = colors[col_name]
            v = _ensure_variant(db, g, size, color, sku_prefix, price)
            all_variants.append(v)
            _ensure_inventory(db, branch_lp, v, 25)
            _ensure_inventory(db, branch_sc, v, 12 if idx % 3 else 5)
    db.commit()

    if not all_variants:
        all_variants = db.query(GarmentVariant).order_by(GarmentVariant.id).all()

    # ---- Promociones (CU-11) ----
    promo_primera = _ensure_promotion(
        db,
        "Primera reserva -10%",
        "Descuento por primera reserva",
        10.0,
        datetime(2026, 9, 1, tzinfo=UTC),
        datetime(2026, 12, 31, tzinfo=UTC),
    )
    promo_hot = _ensure_promotion(
        db,
        "Hot Sale -15%",
        "Descuento especial de temporada",
        15.0,
        datetime(2026, 9, 15, tzinfo=UTC),
        datetime(2026, 10, 31, tzinfo=UTC),
    )
    promo_vencida = _ensure_promotion(
        db,
        "Liquidación de verano",
        "Promoción finalizada",
        30.0,
        datetime(2026, 1, 1, tzinfo=UTC),
        datetime(2026, 3, 31, tzinfo=UTC),
    )
    promo_vencida.status = PromotionStatus.EXPIRED
    # Vincular prendas a las promociones (variedad)
    def _link_garments(promotion: Promotion, garments_to_link: list[Garment]) -> None:
        for g in garments_to_link:
            if g not in promotion.garments:
                promotion.garments.append(g)
    all_garments = db.query(Garment).order_by(Garment.id).all()
    _link_garments(promo_primera, all_garments[:3])
    _link_garments(promo_hot, all_garments[3:7])
    _link_garments(promo_vencida, all_garments[7:10])
    db.commit()

    # ---- Historial de navegación (CU-30) ----
    if db.query(BrowsingHistory).count() == 0:
        for i, v in enumerate(all_variants[:8]):
            db.add(BrowsingHistory(
                client_id=real_client.id,
                variant_id=v.id,
                view_count=3 + (i % 5),
            ))
        for v in all_variants[8:12]:
            db.add(BrowsingHistory(
                client_id=demo_client.id,
                variant_id=v.id,
                view_count=1,
            ))
        db.commit()

    # ---- Carrito demo (CU-20) ----
    existing_cart = db.query(Cart).filter(Cart.client_id == real_client.id).first()
    if not existing_cart:
        cart = Cart(client_id=real_client.id, branch_id=branch_lp.id, is_active=True)
        db.add(cart)
        db.flush()
        for v in all_variants[:2]:
            db.add(CartDetail(
                cart_id=cart.id,
                variant_id=v.id,
                quantity=1,
                unit_price=v.price,
            ))
        db.commit()

    # ---- Recepciones de productos (CU-29) ----
    if db.query(Reception).count() == 0:
        rec1 = Reception(
            supplier_id=supplier.id,
            branch_id=branch_lp.id,
            employee_id=manager_employee.id,
            received_at=datetime(2026, 9, 5, tzinfo=UTC),
            purchase_order_ref=f"PO-SEED-{secrets.token_hex(3).upper()}",
            notes="Recepción de camisas y buzos por Textiles Andinos",
        )
        db.add(rec1)
        db.flush()
        for v in all_variants[:3]:
            db.add(ReceptionDetail(
                reception_id=rec1.id,
                variant_id=v.id,
                quantity=20,
                cost_price=Decimal(str(round(float(v.price) * 0.6, 2))),
            ))
            # Sumar stock en la sucursal (consistente con reception_service)
            inv = db.query(Inventory).filter(
                Inventory.branch_id == branch_lp.id,
                Inventory.variant_id == v.id,
            ).first()
            if inv:
                inv.quantity += 20
        rec2 = Reception(
            supplier_id=supplier.id,
            branch_id=branch_sc.id,
            employee_id=manager_employee.id,
            received_at=datetime(2026, 9, 12, tzinfo=UTC),
            purchase_order_ref=f"PO-SEED-{secrets.token_hex(3).upper()}",
            notes="Recepción de vestidos para Equipetrol",
        )
        db.add(rec2)
        db.flush()
        for v in all_variants[6:8]:
            db.add(ReceptionDetail(
                reception_id=rec2.id,
                variant_id=v.id,
                quantity=15,
                cost_price=Decimal(str(round(float(v.price) * 0.55, 2))),
            ))
            inv = db.query(Inventory).filter(
                Inventory.branch_id == branch_sc.id,
                Inventory.variant_id == v.id,
            ).first()
            if inv:
                inv.quantity += 15
        db.commit()

    # ---- Movimientos de inventario (CU-28) ----
    if db.query(InventoryMovement).count() == 0:
        for v in all_variants[:4]:
            db.add(InventoryMovement(
                branch_id=branch_lp.id,
                variant_id=v.id,
                movement_type=InventoryMovementType.IN,
                quantity=20,
                reason="Recepción de proveedor",
            ))
        db.add(InventoryMovement(
            branch_id=branch_lp.id,
            variant_id=all_variants[0].id,
            movement_type=InventoryMovementType.OUT,
            quantity=4,
            reason="Venta presencial",
        ))
        db.add(InventoryMovement(
            branch_id=branch_sc.id,
            variant_id=all_variants[6].id,
            movement_type=InventoryMovementType.IN,
            quantity=15,
            reason="Recepción de proveedor",
        ))
        db.commit()

    # ---- Reservas demo (CU-15, CU-16, CU-17, CU-18) ----
    if not db.query(Reservation).filter(Reservation.pickup_code.like("DEMO-%")).first():
        now = datetime.now(UTC)

        def mk_reservation(status: ReservationStatus | str, minutes_from: int, code: str) -> Reservation:
            return Reservation(
                client_id=real_client.id,
                branch_id=branch_lp.id,
                status=status.value if isinstance(status, ReservationStatus) else status,
                pickup_code=f"DEMO-{code}",
                expires_at=now + timedelta(minutes=minutes_from),
                total_amount=Decimal("0"),
                notes="Reserva demo generada por seed",
            )

        r_pending = mk_reservation(ReservationStatus.PENDING, 120, "P001")
        r_prepared = mk_reservation(ReservationStatus.PREPARED, 180, "P002")
        r_trial = mk_reservation(ReservationStatus.IN_TRIAL, 240, "P003")
        r_completed = mk_reservation(ReservationStatus.COMPLETED, -1200, "P004")
        r_cancelled = mk_reservation(ReservationStatus.CANCELLED, -600, "P005")
        r_expired = mk_reservation(ReservationStatus.EXPIRED, -1800, "P006")
        db.add_all([r_pending, r_prepared, r_trial, r_completed, r_cancelled, r_expired])
        db.flush()
        for r, vars_to_add in (
            (r_pending, all_variants[:2]),
            (r_prepared, all_variants[1:3]),
            (r_trial, all_variants[2:4]),
            (r_completed, all_variants[4:6]),
            (r_cancelled, all_variants[0:1]),
            (r_expired, all_variants[3:4]),
        ):
            total = Decimal("0")
            for v in vars_to_add:
                db.add(ReservationDetail(
                    reservation_id=r.id,
                    variant_id=v.id,
                    quantity=1,
                    unit_price=v.price,
                ))
                total += v.price
            r.total_amount = total
        db.commit()

    # ---- Historial de estados de reserva (CU-34/17) ----
    if db.query(ReservationHistory).count() == 0:
        reservations = db.query(Reservation).order_by(Reservation.id).all()
        status_order = [
            ReservationStatus.PENDING,
            ReservationStatus.PREPARED,
            ReservationStatus.IN_TRIAL,
            ReservationStatus.COMPLETED,
        ]
        for r in reservations:
            prev = None
            for target in status_order:
                if r.status == ReservationStatus.CANCELLED.value:
                    target = ReservationStatus.CANCELLED
                elif r.status == ReservationStatus.EXPIRED.value:
                    target = ReservationStatus.EXPIRED
                db.add(ReservationHistory(
                    reservation_id=r.id,
                    from_status=prev.value if prev else None,
                    to_status=target.value,
                    changed_by_user_id=cashier_user.id,
                    comment="Cambio de estado",
                ))
                prev = target
                if target == ReservationStatus.CANCELLED or target == ReservationStatus.EXPIRED:
                    break
        db.commit()

    # ---- Ventas histórico variadas (CU-22, CU-24, CU-26, CU-33, CU-35) ----
    if not db.query(Sale).filter(Sale.invoice_number.like("%-SEED-%")).first():
        dates = [
            datetime(2026, 8, 3, tzinfo=UTC),
            datetime(2026, 8, 17, tzinfo=UTC),
            datetime(2026, 8, 29, tzinfo=UTC),
            datetime(2026, 9, 2, tzinfo=UTC),
            datetime(2026, 9, 8, tzinfo=UTC),
            datetime(2026, 9, 15, tzinfo=UTC),
            datetime(2026, 9, 18, tzinfo=UTC),
        ]
        patterns = [
            (all_variants[0:2], "QR"),
            (all_variants[2:4], "card"),
            (all_variants[4:6], "cash"),
            (all_variants[6:7], "QR"),
            (all_variants[8:10], "card"),
            (all_variants[10:12], "cash"),
            (all_variants[1:3], "QR"),
        ]
        for i, (items, method) in enumerate(patterns):
            paid_at = dates[i]
            current_items = [
                (v, (i % 3) + 1)
                for v in (items if isinstance(items, list) else [items])
            ]
            # 1 de cada 4 ventas al cliente demo, el resto al cliente real
            buyer = real_client if i % 4 else demo_client
            employee = cashier_employee if i % 3 else manager_employee
            _make_paid_sale(
                db,
                f"SEED-{i + 1:02d}",
                client=buyer,
                branch=branch_lp if i % 2 == 0 else branch_sc,
                employee=employee,
                items=current_items,
                paid_at=paid_at,
                payment_method=method,
            )
        db.commit()

    # ---- Notificaciones demo (CU-03 UI) ----
    if not db.query(Notification).filter(Notification.user_id == real_client_user.id).first():
        db.add_all([
            Notification(
                user_id=real_client_user.id,
                type="PROMOTION",
                title="Hot Sale -15%",
                body="Descuentos especiales en toda la colección hasta el 31 de octubre.",
                is_read=True,
            ),
            Notification(
                user_id=real_client_user.id,
                type="RESERVATION",
                title="Tu reserva DEMO-P001 está lista",
                body="Ya puedes pasar a probarte tus prendas en Sucursal Sopocachi.",
                is_read=False,
            ),
            Notification(
                user_id=real_client_user.id,
                type="RESERVATION",
                title="Tu reserva está en preparación",
                body="El staff está preparando tus prendas reservadas.",
                is_read=False,
            ),
            Notification(
                user_id=real_client_user.id,
                type="SYSTEM",
                title="Bienvenida FashionStore",
                body="Tu cuenta demo está lista. ¡Explora el catálogo!",
                is_read=False,
            ),
            Notification(
                user_id=cashier_user.id,
                type="STOCK",
                title="Stock bajo",
                body="Algunas variantes tienen stock bajo en Sucursal Sopocachi.",
                is_read=False,
            ),
        ])
        db.commit()

    # ---- Bitácora / trazabilidad (CU-34) ----
    if db.query(AuditLog).count() == 0:
        admin_id = admin_user.id
        manager_id = manager_user.id
        cashier_id = cashier_user.id
        db.add_all([
            AuditLog(user_id=admin_id, action="LOGIN", entity="User", entity_id=admin_id, metadata_json=None),
            AuditLog(user_id=admin_id, action="CREATE", entity="User", entity_id=manager_user.id, metadata_json=None),
            AuditLog(user_id=admin_id, action="CREATE", entity="Product", entity_id=first_garment.id if first_garment else None, metadata_json=None),
            AuditLog(user_id=manager_id, action="CREATE", entity="Promotion", entity_id=promo_hot.id, metadata_json=None),
            AuditLog(user_id=manager_id, action="ADJUST", entity="Inventory", entity_id=None, metadata_json='{"reason": "stock demo"}'),
            AuditLog(user_id=cashier_id, action="CREATE", entity="Reservation", entity_id=None, metadata_json=None),
            AuditLog(user_id=cashier_id, action="PREPARE", entity="Reservation", entity_id=None, metadata_json=None),
            AuditLog(user_id=cashier_id, action="SALE_PAID", entity="Sale", entity_id=None, metadata_json=None),
            AuditLog(user_id=real_client_user.id, action="LOGIN", entity="User", entity_id=real_client_user.id, metadata_json=None),
        ])
        db.commit()

    print("Seeding completed.")
    print("Usuarios demo:")
    for email, password in DEMO_PASSWORDS.items():
        print(f"  {email}  /  {password}")
    print("Cliente demo con email real (recibe correo de recuperación):")
    print(f"  {REAL_CLIENT_EMAIL}  /  Client123!")
    db.close()
    engine.dispose()


if __name__ == "__main__":
    run()
import secrets
from datetime import UTC, date, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine
from app.core.security import hash_password
from app.models.analytics import Promotion
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
from app.models.reservation import Reservation, ReservationDetail, ReservationStatus
from app.models.sales import Payment, Receipt, Sale, SaleDetail, SalePaymentStatus, SaleStatus
from app.models.user import Branch, City, Client, Employee, Role, Supplier, User

# Credenciales demo (NUNCA usar en producciÃ³n).
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
    sku = f"{sku_prefix}-{size.name.upper()}-{color.name.upper()[:2]}-{secrets.token_hex(3).upper()}"
    variant = db.query(GarmentVariant).filter(GarmentVariant.sku == sku).first()
    if not variant:
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
    _ensure_user(db, "admin@fashionstore.dev", DEMO_PASSWORDS["admin@fashionstore.dev"], "ADMIN")
    manager_user = _ensure_user(db, "manager@fashionstore.dev", DEMO_PASSWORDS["manager@fashionstore.dev"], "MANAGER")
    cashier_user = _ensure_user(db, "cashier@fashionstore.dev", DEMO_PASSWORDS["cashier@fashionstore.dev"], "CASHIER")
    demo_client_user = _ensure_user(db, "client@fashionstore.dev", DEMO_PASSWORDS["client@fashionstore.dev"], "CLIENT")
    real_client_user = _ensure_user(db, REAL_CLIENT_EMAIL, DEMO_PASSWORDS[REAL_CLIENT_EMAIL], "CLIENT")
    supplier_user = _ensure_user(db, "supplier@fashionstore.dev", DEMO_PASSWORDS["supplier@fashionstore.dev"], "SUPPLIER")
    db.commit()

    if not db.query(Employee).filter(Employee.user_id == manager_user.id).first():
        db.add(Employee(
            user_id=manager_user.id,
            branch_id=branch_lp.id,
            first_name="Gerente",
            last_name="Demo",
            hire_date=date(2025, 1, 10),
        ))
    if not db.query(Employee).filter(Employee.user_id == cashier_user.id).first():
        db.add(Employee(
            user_id=cashier_user.id,
            branch_id=branch_lp.id,
            first_name="Cajero",
            last_name="Demo",
            hire_date=date(2025, 3, 15),
        ))
    if not db.query(Client).filter(Client.user_id == demo_client_user.id).first():
        db.add(Client(
            user_id=demo_client_user.id,
            first_name="Cliente",
            last_name="Demo",
            birth_date=date(1995, 5, 20),
            points=120,
        ))
    if not db.query(Client).filter(Client.user_id == real_client_user.id).first():
        db.add(Client(
            user_id=real_client_user.id,
            first_name="Cliente",
            last_name="Real",
            birth_date=date(1993, 3, 10),
            points=0,
        ))
    if not db.query(Supplier).filter(Supplier.company_name == "Textiles Andinos SRL").first():
        db.add(Supplier(
            company_name="Textiles Andinos SRL",
            contact_name="Proveedor Demo",
            email=supplier_user.email,
            address="Zona Central, La Paz",
        ))
    db.commit()

    # ---- Catálogo ----
    season = db.query(Season).filter(Season.name == "OtoÃ±o/Invierno 2026").first()
    if not season:
        season = Season(name="OtoÃ±o/Invierno 2026")
        db.add(season)
        db.flush()
    collection = db.query(Collection).filter(Collection.name == "ColecciÃ³n Urbana").first()
    if not collection:
        collection = Collection(season_id=season.id, name="ColecciÃ³n Urbana", launch_year=2026)
        db.add(collection)
        db.flush()

    cat_camisas = _ensure_category(db, "Camisas", "Prendas formales y casuales")
    cat_poleras = _ensure_category(db, "Poleras", "Hoodies y buzos para el dia a dia")
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
        ("Camisa Oxford BÃ¡sica", cat_camisas, "Camisa de algodÃ³n, corte regular.", 180.0, True),
        ("Camisa Slim Rayas", cat_camisas, "Camisa slim con rayas sutiles.", 220.0, False),
        ("Hoodie Urban Core", cat_poleras, "Hoodie de algodÃ³n grueso con capucha.", 260.0, True),
        ("Buzo Classic", cat_poleras, "Buzo clÃ¡sico con bolsillo canguro.", 240.0, False),
        ("PantalÃ³n Chino Slim", cat_pantalones, "Chino slim para todas las ocasiones.", 200.0, False),
        ("Jeans Skinny", cat_pantalones, "Denim elÃ¡stico corte skinny.", 245.0, False),
        ("Vestido Casual", cat_vestidos, "Vestido casual de algodÃ³n.", 290.0, True),
        ("Vestido Largo", cat_vestidos, "Vestido largo estilo bohemio.", 350.0, True),
        ("Chaqueta Denim", cat_chaquetas, "Casaca de jean clÃ¡sica.", 320.0, True),
        ("Rompevientos Ligero", cat_chaquetas, "Chaqueta rompevientos impermeable.", 310.0, False),
    ]

    first_garment = None
    for name, cat, desc, price, is_ar in garments:
        g = _ensure_garment(db, cat, collection, name, desc, price, is_ar)
        first_garment = first_garment or g
        sku_prefix = "".join(ch for ch in name.upper().split()[0] if ch.isalnum())
        # Variantes: 2 combinaciones talla/color por prenda
        combos = [("S", "Negro"), ("M", "Blanco"), ("L", "Azul"), ("XL", "Rojo")]
        for idx, (sz, col) in enumerate(combos[:2]):
            size = sizes[sz]
            color = colors[col]
            v = _ensure_variant(db, g, size, color, sku_prefix, price)
            _ensure_inventory(db, branch_lp, v, 25 if idx == 0 else 18)
            _ensure_inventory(db, branch_sc, v, 12)
    db.commit()

    promotion = db.query(Promotion).first()
    if not promotion:
        promotion = Promotion(
            name="Primera reserva -10%",
            description="Descuento por primera reserva",
            discount_percent=10.0,
            start_at=datetime(2026, 9, 1),
            end_at=datetime(2026, 12, 31),
        )
        db.add(promotion)
        db.flush()
    if first_garment is not None and first_garment not in promotion.garments:
        promotion.garments.append(first_garment)
    db.commit()

    # ---- Datos demo para flujos (reservas + venta POS) ----
    real_client = db.query(Client).filter(Client.user_id == real_client_user.id).first()
    cashier_employee = db.query(Employee).filter(Employee.user_id == cashier_user.id).first()

    variant_a = (
        first_garment.variations[0] if first_garment is not None and first_garment.variations
        else db.query(GarmentVariant).first()
    )

    if real_client is not None and not db.query(Reservation).filter(
        Reservation.pickup_code.like("DEMO-%")
    ).first():
        now = datetime.now(UTC)

        def mk_reservation(status: str | ReservationStatus, hours_ago: int, code: str) -> Reservation:
            return Reservation(
                client_id=real_client.id,
                branch_id=branch_lp.id,
                status=status.value if isinstance(status, ReservationStatus) else status,
                pickup_code=f"DEMO-{code}",
                expires_at=now + timedelta(hours=hours_ago),
                total_amount=variant_a.price if variant_a else 0,
                notes="Reserva demo generada por seed",
            )
        r_pending = mk_reservation(ReservationStatus.PENDING, 2, "P001")
        r_prepared = mk_reservation(ReservationStatus.PREPARED, 3, "P002")
        r_trial = mk_reservation(ReservationStatus.IN_TRIAL, 4, "P003")
        db.add_all([r_pending, r_prepared, r_trial])
        db.flush()
        for r in (r_pending, r_prepared, r_trial):
            if variant_a is not None:
                db.add(ReservationDetail(
                    reservation_id=r.id,
                    variant_id=variant_a.id,
                    quantity=1,
                    unit_price=variant_a.price,
                ))
        db.commit()

    if (
        real_client is not None
        and variant_a is not None
        and not db.query(Sale).filter(Sale.invoice_number.like("DEMO-%")).first()
    ):
        sale = Sale(
            invoice_number=f"DEMO-{secrets.token_hex(4).upper()}",
            client_id=real_client.id,
            branch_id=branch_lp.id,
            employee_id=cashier_employee.id if cashier_employee else None,
            total_amount=variant_a.price,
            payment_method="QR",
            status=SaleStatus.PAID,
            paid_at=datetime.now(UTC),
        )
        db.add(sale)
        db.flush()
        db.add(SaleDetail(
            sale_id=sale.id,
            variant_id=variant_a.id,
            quantity=1,
            unit_price=variant_a.price,
        ))
        db.add(Payment(
            sale_id=sale.id,
            gateway_reference=f"DEMO-QR-{secrets.token_hex(4).upper()}",
            amount=variant_a.price,
            currency="BOB",
            method="QR",
            status=SalePaymentStatus.COMPLETED,
        ))
        db.add(Receipt(
            sale_id=sale.id,
            type="invoice",
            rnc_or_cuf=None,
            document_url=None,
        ))
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

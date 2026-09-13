import secrets
from datetime import date, datetime

from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine
from app.core.security import hash_password
from app.models.analytics import Promotion
from app.models.catalog import Category, Collection, Color, Garment, GarmentVariant, Season, Size
from app.models.inventory import Inventory
from app.models.user import Branch, City, Client, Employee, Role, Supplier, User

# Credenciales demo (NUNCA usar en producción).
DEMO_PASSWORDS = {
    "admin@fashionstore.test": "Admin123!",
    "manager@fashionstore.test": "Manager123!",
    "cashier@fashionstore.test": "Cashier123!",
    "client@fashionstore.test": "Client123!",
    "supplier@fashionstore.test": "Supplier123!",
}


def _ensure_user(db: Session, email: str, password: str, role_name: str) -> User:
    user = db.query(User).filter(User.email == email.lower()).first()
    if not user:
        user = User(email=email.lower(), password_hash=hash_password(password))
        db.add(user)
    role = db.query(Role).filter(Role.name == role_name).first()
    if role and role not in user.roles:
        user.roles.append(role)
    return user


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

    branch = db.query(Branch).filter(Branch.name == "Sucursal Sopocachi").first()
    if not branch:
        branch = Branch(city_id=la_paz.id, name="Sucursal Sopocachi", address="Av. 6 de Agosto 1234")
        db.add(branch)
    db.commit()

    _ensure_user(db, "admin@fashionstore.test", DEMO_PASSWORDS["admin@fashionstore.test"], "ADMIN")
    manager_user = _ensure_user(db, "manager@fashionstore.test", DEMO_PASSWORDS["manager@fashionstore.test"], "MANAGER")
    _ensure_user(db, "cashier@fashionstore.test", DEMO_PASSWORDS["cashier@fashionstore.test"], "CASHIER")
    client_user = _ensure_user(db, "client@fashionstore.test", DEMO_PASSWORDS["client@fashionstore.test"], "CLIENT")
    supplier_user = _ensure_user(db, "supplier@fashionstore.test", DEMO_PASSWORDS["supplier@fashionstore.test"], "SUPPLIER")
    db.commit()

    if not db.query(Employee).filter(Employee.user_id == manager_user.id).first():
        db.add(Employee(
            user_id=manager_user.id,
            branch_id=branch.id,
            first_name="Gerente",
            last_name="Demo",
            hire_date=date(2025, 1, 10),
        ))
    if not db.query(Client).filter(Client.user_id == client_user.id).first():
        db.add(Client(
            user_id=client_user.id,
            first_name="Cliente",
            last_name="Demo",
            birth_date=date(1995, 5, 20),
            points=120,
        ))
    if not db.query(Supplier).filter(Supplier.company_name == "Textiles Andinos SRL").first():
        db.add(Supplier(
            company_name="Textiles Andinos SRL",
            contact_name="Proveedor Demo",
            email=supplier_user.email,
            address="Zona Central, La Paz",
        ))
    db.commit()

    season = db.query(Season).filter(Season.name == "Otoño/Invierno 2026").first()
    if not season:
        season = Season(name="Otoño/Invierno 2026")
        db.add(season)
        db.commit()
    collection = db.query(Collection).filter(Collection.name == "Colección Urbana").first()
    if not collection:
        collection = Collection(season_id=season.id, name="Colección Urbana", launch_year=2026)
        db.add(collection)
        db.commit()

    category = db.query(Category).filter(Category.name == "Camisas").first()
    if not category:
        category = Category(name="Camisas", description="Prendas formales y casuales")
        db.add(category)
        db.commit()

    size_s = db.query(Size).filter(Size.name == "S").first() or Size(name="S")
    size_m = db.query(Size).filter(Size.name == "M").first() or Size(name="M")
    db.add_all([size_s, size_m])
    color_negro = db.query(Color).filter(Color.name == "Negro").first() or Color(name="Negro", hex_code="#000000")
    color_blanco = db.query(Color).filter(Color.name == "Blanco").first() or Color(name="Blanco", hex_code="#FFFFFF")
    db.add_all([color_negro, color_blanco])
    db.commit()

    if not db.query(Garment).filter(Garment.name == "Camisa Oxford Básica").first():
        garment = Garment(
            category_id=category.id,
            collection_id=collection.id,
            name="Camisa Oxford Básica",
            description="Camisa de algodón, corte regular.",
            base_price=180.0,
            is_ar_enabled=True,
        )
        db.add(garment)
        db.commit()
        v1 = GarmentVariant(garment_id=garment.id, size_id=size_s.id, color_id=color_negro.id,
                            sku=f"CAM-OXF-S-N-{secrets.token_hex(3).upper()}", price=180.0)
        v2 = GarmentVariant(garment_id=garment.id, size_id=size_m.id, color_id=color_blanco.id,
                            sku=f"CAM-OXF-M-B-{secrets.token_hex(3).upper()}", price=180.0)
        db.add_all([v1, v2])
        db.commit()
        for v in (v1, v2):
            db.add(Inventory(branch_id=branch.id, variant_id=v.id, quantity=25))
        db.commit()

    if not db.query(Promotion).first():
        db.add(Promotion(
            name="Primera reserva -10%",
            description="Descuento por primera reserva",
            discount_percent=10.0,
            start_at=datetime(2026, 9, 1),
            end_at=datetime(2026, 12, 31),
        ))
        db.commit()

    print("Seeding completed.")
    print("Usuarios demo:")
    for email, password in DEMO_PASSWORDS.items():
        print(f"  {email}  /  {password}")
    db.close()
    engine.dispose()


if __name__ == "__main__":
    run()

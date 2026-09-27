"""Checkout tests: SQLite only, no application seed or migrations.

Keep outside tests/ so its PostgreSQL/seed conftest is never loaded.
"""
import os

# Set before importing any application modules; never inherit the project's DB.
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["TEST_DATABASE_URL"] = "sqlite://"
os.environ["PAYMENT_GATEWAY"] = "mock"
os.environ["SECRET_KEY"] = "isolated-checkout-test-key-not-for-production"
os.environ["SMTP_HOST"] = ""
os.environ["DEBUG"] = "false"

import pytest
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from app.api.v1.routes_cart import router as cart_router
from app.api.v1.routes_sales import router as sales_router
from app.core.database import Base, get_db
from app.core.exceptions import AppError
from app.core.security import create_access_token
from app.models import Branch, Category, City, Client, Color, Garment, GarmentVariant, Inventory, Size, User
from app.payments.api.v1.payments import router as payments_router
from app.payments.factory import get_payment_service


@pytest.fixture
def checkout_api(tmp_path):
    engine = create_engine(f"sqlite:///{(tmp_path / 'checkout.sqlite').as_posix()}",
                           connect_args={"check_same_thread": False})
    assert engine.url.get_backend_name() == "sqlite"

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    with Session(engine, expire_on_commit=False) as db:
        user = User(email="owner@example.test", password_hash="unused")
        other = User(email="other@example.test", password_hash="unused")
        owner = Client(user=user, first_name="Test", last_name="Owner")
        branch = Branch(city=City(name="Test", state="Test"), name="Test", address="Test")
        variant = GarmentVariant(
            garment=Garment(category=Category(name="Test"), name="Test shirt", base_price=25),
            size=Size(name="M"), color=Color(name="Blue"), sku="TEST-1", price=25,
        )
        db.add_all([owner, other, Inventory(branch=branch, variant=variant, quantity=10)])
        db.commit()
        app = FastAPI()

        @app.exception_handler(AppError)
        async def handle_error(request, exc):
            return JSONResponse(status_code=exc.status_code, content={"message": exc.message})

        def test_db():
            yield db

        app.dependency_overrides[get_db] = test_db
        for router in (cart_router, sales_router, payments_router):
            app.include_router(router, prefix="/api/v1")
        get_payment_service.cache_clear()
        with TestClient(app) as client:
            yield client, db, user, other, branch, variant
        get_payment_service.cache_clear()
    engine.dispose()


def auth(user):
    return {"Authorization": f"Bearer {create_access_token(str(user.id))}"}

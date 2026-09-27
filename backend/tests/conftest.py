import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import (
    Base,
    engine,
    reset_active_session,
    set_active_session,
    set_engine_override,
)
from app.main import app
from app.models.analytics import BrowsingHistory, Notification
from app.models.cart import Cart, CartDetail  # noqa: F401
from app.models.inventory import Inventory  # noqa: F401
from app.models.user import Client, Employee, PasswordReset, User

# Schema aislado en la misma base. Evita que la suite escriba en los datos
# reales; se puede usar una base totalmente aparte con TEST_DATABASE_URL.
TEST_SCHEMA = "fashionstore_test"


def _build_test_engine():
    if url := os.environ.get("TEST_DATABASE_URL"):
        return create_engine(url, pool_pre_ping=True), None

    raw = create_engine(engine.url, pool_pre_ping=True)
    with raw.connect() as conn:
        conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{TEST_SCHEMA}"'))
        conn.commit()
    return raw.execution_options(schema_translate_map={None: TEST_SCHEMA}), raw


TEST_ENGINE, RAW_TEST_ENGINE = _build_test_engine()


def _build_raw_sql_engine():
    """Engine para el SQL crudo de pgvector.

    ``schema_translate_map`` no aplica a texto SQL plano, asi que aqui hace
    falta fijar el ``search_path`` de cada conexion al schema de pruebas. De lo
    contrario el backfill de embeddings escribiria en los datos reales.
    """
    if url := os.environ.get("TEST_DATABASE_URL"):
        return create_engine(url, pool_pre_ping=True)

    eng = create_engine(engine.url, pool_pre_ping=True)

    @event.listens_for(eng, "connect")
    def _use_test_schema(dbapi_conn, _record):  # pragma: no cover - hook de driver
        with dbapi_conn.cursor() as cur:
            # El schema de pruebas primero para las tablas; ``public`` se mantiene
            # porque ahi vive la extension ``vector`` (clase de operadores).
            cur.execute(f'SET search_path TO "{TEST_SCHEMA}", public')

    return eng


RAW_SQL_TEST_ENGINE = _build_raw_sql_engine()


@pytest.fixture(scope="session", autouse=True)
def _prepare_test_database():
    """Crea el schema de pruebas desde cero y lo siembra una vez por sesion."""
    from scripts import seed

    # El SQL crudo (pgvector) debe escribir en el schema de pruebas.
    set_engine_override(RAW_SQL_TEST_ENGINE)

    if RAW_TEST_ENGINE is not None:
        with RAW_TEST_ENGINE.connect() as conn:
            conn.execute(text(f'DROP SCHEMA IF EXISTS "{TEST_SCHEMA}" CASCADE'))
            conn.execute(text(f'CREATE SCHEMA "{TEST_SCHEMA}"'))
            conn.commit()

    Base.metadata.drop_all(TEST_ENGINE)
    Base.metadata.create_all(TEST_ENGINE)

    session = sessionmaker(bind=TEST_ENGINE, autocommit=False, autoflush=False)()
    try:
        seed.run(session, quiet=True)
        session.commit()
    finally:
        session.close()
    yield
    TEST_ENGINE.dispose()
    RAW_SQL_TEST_ENGINE.dispose()


@pytest.fixture(autouse=True)
def db():
    """Aísla cada test en una transacción que se revierte al terminar.

    ``join_transaction_mode="create_savepoint"`` convierte los commit() de los
    servicios en savepoints, de modo que un commit de negocio no confirma de
    verdad la transacción externa.
    """
    connection = TEST_ENGINE.connect()
    transaction = connection.begin()
    session = Session(
        bind=connection,
        autocommit=False,
        autoflush=False,
        join_transaction_mode="create_savepoint",
    )
    token = set_active_session(session)
    try:
        yield session
    finally:
        reset_active_session(token)
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client():
    c = TestClient(app)
    yield c




def _login_headers(client, email, password):
    r = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def admin_headers(client):
    return _login_headers(client, "admin@fashionstore.dev", "Admin123!")


@pytest.fixture
def client_headers(client):
    return _login_headers(client, "client@fashionstore.dev", "Client123!")


def unique_email(prefix: str = "test-cu01") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}@fashionstore.dev"


@pytest.fixture
def cleanup_users(db):
    """Registra correos creados por un test para borrarlos dentro de su
    transaccion (el rollback de ``db`` ya se encarga al final)."""
    created: list[str] = []

    def _track(email: str) -> str:
        created.append(email)
        return email

    yield _track

    for email in created:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            continue
        db.query(Notification).filter(Notification.user_id == user.id).delete()
        db.query(PasswordReset).filter(PasswordReset.user_id == user.id).delete()
        client = db.query(Client).filter(Client.user_id == user.id).first()
        if client:
            db.query(BrowsingHistory).filter(BrowsingHistory.client_id == client.id).delete()
        db.query(Employee).filter(Employee.user_id == user.id).delete()
        db.delete(user)
    db.flush()


"""Stock integration tests using independent PostgreSQL sessions and a disposable schema."""
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, date, datetime, timedelta
from threading import Event
from time import monotonic, sleep
from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateSchema, DropSchema

from app.core.database import Base
from app.core.exceptions import ConflictError, ValidationError
from app.models import (
    Branch,
    Category,
    City,
    Client,
    Color,
    Garment,
    GarmentVariant,
    Inventory,
    Size,
    User,
)
from app.models.movement import InventoryMovement, InventoryMovementType
from app.models.reservation import Reservation
from app.models.sales import Payment, Receipt, Sale
from app.models.user import Employee, Supplier
from app.payments.api.v1.payments import confirm_payment
from app.schemas.inventory import InventoryAdjust
from app.schemas.payment import PaymentConfirm
from app.schemas.reception import ReceptionCreate
from app.schemas.reservation import ReservationCreate
from app.schemas.sale import SaleGenerate
from app.services.inventory_service import inventory_service
from app.services.reception_service import reception_service
from app.services.reservation_service import reservation_service
from app.services.sales_service import sales_service
from app.tasks import inventory_sync, reservation_expiry


@pytest.fixture
def stock_db(db):
    source = db.get_bind().engine
    assert source.dialect.name == "postgresql", "Real PostgreSQL is required"
    assert source.url.host in {"localhost", "127.0.0.1", "postgres"}, "Local/CI only"
    schema = "stock_test_" + uuid4().hex
    engine = create_engine(source.url, execution_options={"schema_translate_map": {None: schema}})
    with engine.begin() as connection:
        connection.execute(CreateSchema(schema))
    try:
        Base.metadata.create_all(engine)
        with Session(engine) as session:
            branch = Branch(city=City(name="Test", state="Test"), name="Test", address="Test")
            clients = [Client(user=User(email=f"client{i}@example.test", password_hash="unused"),
                              first_name="Test", last_name=str(i)) for i in range(2)]
            garment = Garment(category=Category(name="Test"), name="Test", base_price=25)
            size, color = Size(name="M"), Color(name="Blue")
            variants = [GarmentVariant(garment=garment, size=size, color=color,
                                       sku=f"TEST-{i}", price=25) for i in range(2)]
            session.add_all(clients + [Inventory(branch=branch, variant=v, quantity=1)
                                       for v in variants])
            session.commit()
            ids = branch.id, [v.id for v in variants], [c.id for c in clients]
        yield engine, *ids
    finally:
        with engine.begin() as connection:
            connection.execute(DropSchema(schema, cascade=True))
        engine.dispose()


def reserve(session, branch, client, items):
    return reservation_service.create(session, client, ReservationCreate(
        branch_id=branch, items=[{"variant_id": variant, "quantity": qty}
                                 for variant, qty in items],
    ))


def stock_counts(stock_db):
    engine, branch, variants, _ = stock_db
    with Session(engine) as session:
        rows = session.query(Inventory).filter(Inventory.branch_id == branch).all()
        return {v: (next(r for r in rows if r.variant_id == v).quantity,
                    next(r for r in rows if r.variant_id == v).reserved_quantity)
                for v in variants}


def compete(stock_db, first, second):
    """Pause one transaction after FOR UPDATE; confirm the other waits in PostgreSQL."""
    engine, *_ = stock_db
    locked, release, second_ready = Event(), Event(), Event()
    pids = {}

    def pause_after_lock(conn, cursor, statement, parameters, context, executemany):
        if (conn.info.get("stock_worker") == 0 and "FOR UPDATE" in statement
                and "inventario" in statement and not locked.is_set()):
            locked.set()
            assert release.wait(15), "Timed out holding the inventory lock"

    def worker(index, operation):
        with Session(engine, autoflush=False) as session:
            connection = session.connection()
            worker_info = connection.info
            worker_info["stock_worker"] = index
            pids[index] = session.scalar(text("SELECT pg_backend_pid()"))
            session.execute(text("SET LOCAL lock_timeout = '10s'"))
            assert session.query(Inventory).all()  # pre-load stale ORM state
            if index == 1:
                second_ready.set()
            try:
                operation(session)
                return "ok"
            except (ValidationError, ConflictError):
                return "rejected"
            finally:
                worker_info.pop("stock_worker", None)

    event.listen(engine, "after_cursor_execute", pause_after_lock)
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            winner = pool.submit(worker, 0, first)
            try:
                assert locked.wait(10), "No inventory lock was acquired"
                loser = pool.submit(worker, 1, second)
                assert second_ready.wait(10)
                deadline = monotonic() + 5
                blocked = False
                with engine.connect() as observer:
                    while monotonic() < deadline:
                        blocked = bool(observer.scalar(
                            text("SELECT cardinality(pg_blocking_pids(:pid)) > 0"),
                            {"pid": pids[1]},
                        ))
                        if blocked:
                            break
                        sleep(0.05)
                assert blocked, "Second PostgreSQL session did not wait for the lock"
            finally:
                release.set()
            return winner.result(timeout=15), loser.result(timeout=15)
    finally:
        release.set()
        event.remove(engine, "after_cursor_execute", pause_after_lock)


def test_last_unit_only_one_reservation_succeeds(stock_db):
    engine, branch, variants, clients = stock_db
    results = compete(stock_db,
        lambda s: reserve(s, branch, clients[0], [(variants[0], 1)]),
        lambda s: reserve(s, branch, clients[1], [(variants[0], 1)]))
    assert results == ("ok", "rejected")
    assert stock_counts(stock_db)[variants[0]] == (1, 1)
    with Session(engine) as session:
        assert session.query(Reservation).count() == 1


def test_opposite_item_order_does_not_deadlock_or_partially_reserve(stock_db):
    engine, branch, variants, clients = stock_db
    results = compete(stock_db,
        lambda s: reserve(s, branch, clients[0], [(variants[0], 1), (variants[1], 1)]),
        lambda s: reserve(s, branch, clients[1], [(variants[1], 1), (variants[0], 1)]))
    assert results == ("ok", "rejected")
    assert stock_counts(stock_db) == {variants[0]: (1, 1), variants[1]: (1, 1)}
    with Session(engine) as session:
        assert session.query(Reservation).count() == 1


def test_duplicate_variant_is_checked_as_one_quantity(stock_db):
    engine, branch, variants, clients = stock_db
    with Session(engine) as session, pytest.raises(ValidationError):
        reserve(session, branch, clients[0], [(variants[0], 1), (variants[0], 1)])
    assert stock_counts(stock_db)[variants[0]] == (1, 0)
    with Session(engine) as session:
        assert session.query(Reservation).count() == 0


def test_multi_item_reservation_and_sale_fail_atomically(stock_db):
    engine, branch, variants, clients = stock_db
    with Session(engine) as session, pytest.raises(ValidationError):
        reserve(session, branch, clients[0], [(variants[0], 1), (variants[1], 2)])
    assert stock_counts(stock_db) == {v: (1, 0) for v in variants}
    with Session(engine) as session, pytest.raises(ValidationError):
        sales_service.create_sale(session, SaleGenerate(branch_id=branch, items=[
            {"variant_id": variants[0], "quantity": 1},
            {"variant_id": variants[1], "quantity": 2},
        ]), client_id=clients[0])
    assert stock_counts(stock_db) == {v: (1, 0) for v in variants}
    with Session(engine) as session:
        assert session.query(Reservation).count() == session.query(Sale).count() == 0


def test_cancel_releases_once(stock_db):
    engine, branch, variants, clients = stock_db
    with Session(engine) as session:
        reservation = reserve(session, branch, clients[0], [(variants[0], 1)])
        reservation_id = reservation.id
        reservation_service.transition(session, reservation, "CANCELLED")
        with pytest.raises(ConflictError):
            reservation_service.transition(session, reservation, "CANCELLED")
        assert session.get(Reservation, reservation_id).status == "CANCELLED"
    assert stock_counts(stock_db)[variants[0]] == (1, 0)


def test_expiry_releases_once(stock_db):
    engine, branch, variants, clients = stock_db
    with Session(engine) as session:
        reservation = reserve(session, branch, clients[0], [(variants[0], 1)])
        reservation.expires_at = datetime.now(UTC) - timedelta(minutes=1)
        session.commit()
        reservation_service.expire(session, reservation)
        with pytest.raises(ConflictError):
            reservation_service.expire(session, reservation)
        assert reservation.status == "EXPIRED"
    assert stock_counts(stock_db)[variants[0]] == (1, 0)


def test_sale_of_reservation_consumes_quantity_and_reserved_once(stock_db):
    engine, branch, variants, clients = stock_db
    with Session(engine) as session:
        reservation = reserve(session, branch, clients[0], [(variants[0], 1)])
        sale = sales_service.create_sale(session, SaleGenerate(
            branch_id=branch, reservation_id=reservation.id), client_id=clients[0])
        assert sale.status == "PENDING"
        assert reservation.status == "COMPLETED"
    assert stock_counts(stock_db)[variants[0]] == (0, 0)


def test_sale_and_reservation_compete_for_last_unit(stock_db):
    engine, branch, variants, clients = stock_db
    results = compete(stock_db,
        lambda s: reserve(s, branch, clients[0], [(variants[0], 1)]),
        lambda s: sales_service.create_sale(s, SaleGenerate(branch_id=branch, items=[
            {"variant_id": variants[0], "quantity": 1}]), client_id=clients[1]))
    assert results == ("ok", "rejected")
    assert stock_counts(stock_db)[variants[0]] == (1, 1)
    with Session(engine) as session:
        assert session.query(Sale).count() == 0


@pytest.mark.parametrize("sale_first", [True, False])
def test_sale_and_cancel_reservation_serialize(stock_db, sale_first):
    engine, branch, variants, clients = stock_db
    with Session(engine) as session:
        reservation_id = reserve(session, branch, clients[0], [(variants[0], 1)]).id

    def sale(session):
        sales_service.create_sale(session, SaleGenerate(
            branch_id=branch, reservation_id=reservation_id), client_id=clients[0])

    def cancel(session):
        reservation_service.transition(session, session.get(Reservation, reservation_id), "CANCELLED")

    assert compete(stock_db, sale if sale_first else cancel, cancel if sale_first else sale) == (
        "ok", "rejected")
    assert stock_counts(stock_db)[variants[0]] == ((0, 0) if sale_first else (1, 0))
    with Session(engine) as session:
        assert session.get(Reservation, reservation_id).status == (
            "COMPLETED" if sale_first else "CANCELLED")
        assert session.query(Sale).count() == int(sale_first)


def test_adjustment_cannot_remove_reserved_unit(stock_db):
    engine, branch, variants, clients = stock_db
    with Session(engine) as session:
        reserve(session, branch, clients[0], [(variants[0], 1)])
        with pytest.raises(ValidationError):
            inventory_service.adjust(session, branch, variants[0], InventoryAdjust(quantity=-1))
    assert stock_counts(stock_db)[variants[0]] == (1, 1)


def test_adjustment_competes_with_reservation(stock_db):
    _, branch, variants, clients = stock_db
    assert compete(stock_db,
        lambda s: reserve(s, branch, clients[0], [(variants[0], 1)]),
        lambda s: inventory_service.adjust(s, branch, variants[0], InventoryAdjust(quantity=-1)),
    ) == ("ok", "rejected")
    assert stock_counts(stock_db)[variants[0]] == (1, 1)


def test_adjustment_creates_missing_branch_stock(stock_db):
    engine, branch, variants, _ = stock_db
    with Session(engine) as session:
        other = Branch(city_id=session.get(Branch, branch).city_id,
                       name="Other branch", address="Other")
        session.add(other)
        session.commit()
        inventory_service.adjust(session, other.id, variants[0], InventoryAdjust(quantity=2))
        row = session.query(Inventory).filter_by(
            branch_id=other.id, variant_id=variants[0]).one()
        assert (row.quantity, row.reserved_quantity) == (2, 0)


def test_reception_and_reservation_serialize(stock_db):
    engine, branch, variants, clients = stock_db
    with Session(engine) as session:
        employee = Employee(user=User(email="receiver@example.test", password_hash="unused"),
                            branch_id=branch, first_name="Test", last_name="Receiver",
                            hire_date=date.today())
        supplier = Supplier(company_name="Concurrent supplier")
        session.add_all([employee, supplier])
        session.commit()
        employee_id, supplier_id = employee.id, supplier.id

    def receive(session):
        reception_service.create(session, ReceptionCreate(
            supplier_id=supplier_id, employee_id=employee_id, branch_id=branch,
            items=[{"variant_id": variants[0], "quantity": 1, "cost_price": 10}],
        ))

    assert compete(stock_db, receive,
        lambda s: reserve(s, branch, clients[0], [(variants[0], 2)])) == ("ok", "ok")
    assert stock_counts(stock_db)[variants[0]] == (2, 2)


def test_adjustment_in_then_sync_does_not_double_count(stock_db, monkeypatch):
    engine, branch, variants, _ = stock_db
    with Session(engine) as session:
        stock = session.query(Inventory).filter_by(variant_id=variants[0]).one()
        stock.quantity = 10
        session.commit()
        inventory_service.adjust(session, branch, variants[0], InventoryAdjust(quantity=3))
    assert stock_counts(stock_db)[variants[0]] == (13, 0)
    monkeypatch.setattr(inventory_sync, "SessionLocal", lambda: Session(engine))
    assert inventory_sync.sync_inventory() == 0
    assert stock_counts(stock_db)[variants[0]] == (13, 0)
    with Session(engine) as session:
        movement = session.query(InventoryMovement).one()
        assert movement.movement_type == InventoryMovementType.IN
        assert movement.is_applied is True


def test_reception_then_sync_does_not_double_count(stock_db, monkeypatch):
    engine, branch, variants, _ = stock_db
    with Session(engine) as session:
        employee = Employee(user=User(email="staff@example.test", password_hash="unused"),
                            branch_id=branch, first_name="Test", last_name="Staff",
                            hire_date=date.today())
        supplier = Supplier(company_name="Test supplier")
        session.add_all([employee, supplier])
        session.commit()
        reception_service.create(session, ReceptionCreate(
            supplier_id=supplier.id, employee_id=employee.id, branch_id=branch,
            items=[{"variant_id": variants[0], "quantity": 2, "cost_price": 10}],
        ))
    assert stock_counts(stock_db)[variants[0]] == (3, 0)
    monkeypatch.setattr(inventory_sync, "SessionLocal", lambda: Session(engine))
    assert inventory_sync.sync_inventory() == 0
    assert stock_counts(stock_db)[variants[0]] == (3, 0)


def test_queued_in_movement_applies_once(stock_db, monkeypatch):
    engine, branch, variants, _ = stock_db
    with Session(engine) as session:
        session.add(InventoryMovement(branch_id=branch, variant_id=variants[0],
            movement_type=InventoryMovementType.IN, quantity=3, is_applied=False))
        session.commit()
    monkeypatch.setattr(inventory_sync, "SessionLocal", lambda: Session(engine))
    assert inventory_sync.sync_inventory() == 1
    assert inventory_sync.sync_inventory() == 0
    assert stock_counts(stock_db)[variants[0]] == (4, 0)
    with Session(engine) as session:
        assert session.query(InventoryMovement).one().is_applied is True


def test_expiry_task_releases_stock_only_once(stock_db, monkeypatch):
    engine, branch, variants, clients = stock_db
    with Session(engine) as session:
        reservation = reserve(session, branch, clients[0], [(variants[0], 1)])
        reservation.expires_at = datetime.now(UTC) - timedelta(minutes=1)
        session.commit()
        reservation_id = reservation.id
    monkeypatch.setattr(reservation_expiry, "SessionLocal", lambda: Session(engine))
    assert reservation_expiry.expire_reservations() == 1
    assert reservation_expiry.expire_reservations() == 0
    assert stock_counts(stock_db)[variants[0]] == (1, 0)
    with Session(engine) as session:
        assert session.get(Reservation, reservation_id).status == "EXPIRED"


@pytest.fixture(params=[False, True], ids=["direct", "reservation"])
def pending_payment_sale(stock_db, request):
    engine, branch, variants, clients = stock_db
    with Session(engine) as session:
        stock = session.query(Inventory).filter_by(variant_id=variants[0]).one()
        stock.quantity = 2
        session.commit()
        other_id = reserve(session, branch, clients[1], [(variants[0], 1)]).id
        own = reserve(session, branch, clients[0], [(variants[0], 1)]) if request.param else None
        reservation_id = own.id if own else None
        sale = sales_service.create_sale(session, SaleGenerate(
            branch_id=branch, reservation_id=reservation_id,
            items=None if own else [{"variant_id": variants[0], "quantity": 1}],
        ), client_id=clients[0])
        ref = "mock_" + uuid4().hex
        session.add(Payment(sale_id=sale.id, gateway_reference=ref, amount=sale.total_amount,
                            method="mock", status="PENDING"))
        session.commit()
        return sale.id, ref, reservation_id, other_id


def confirm_stock_payment(session, ref, status):
    payment = session.query(Payment).filter_by(gateway_reference=ref).one()
    user = session.get(Client, payment.sale.client_id).user
    gateway = SimpleNamespace(status=lambda _: SimpleNamespace(status=status))
    return confirm_payment(session, PaymentConfirm(gateway_reference=ref), gateway, user)


def assert_payment_stock(stock_db, attempt, status):
    engine, _, variants, _ = stock_db
    sale_id, ref, reservation_id, other_id = attempt
    with Session(engine) as session:
        inventory = session.query(Inventory).filter_by(variant_id=variants[0]).one()
        assert (inventory.quantity, inventory.reserved_quantity) == (
            2 if status == "DECLINED" else 1, 1)
        assert session.get(Reservation, other_id).status == "PENDING"
        if reservation_id:
            assert session.get(Reservation, reservation_id).status == (
                "CANCELLED" if status == "DECLINED" else "COMPLETED")
        sale = session.get(Sale, sale_id)
        assert sale.status == (
            "CANCELLED" if status == "DECLINED"
            else "PAID" if status == "COMPLETED" else "PENDING")
        assert (sale.paid_at is not None) == (status == "COMPLETED")
        assert session.query(Payment).filter_by(gateway_reference=ref).one().status == status
        assert session.query(Receipt).filter_by(sale_id=sale_id).count() == int(status == "COMPLETED")
        assert session.query(Sale).count() == 1


@pytest.mark.parametrize("status", ["PENDING", "COMPLETED", "DECLINED", "TIMEOUT"])
def test_payment_stock_transition_and_retry(stock_db, pending_payment_sale, status):
    engine, branch, variants, clients = stock_db
    _, ref, _, _ = pending_payment_sale
    for _ in range(2):
        with Session(engine) as session:
            assert confirm_stock_payment(session, ref, status)["status"] == status
        assert_payment_stock(stock_db, pending_payment_sale, status)
    if status != "DECLINED":
        with Session(engine) as session, pytest.raises(ValidationError):
            sales_service.create_sale(session, SaleGenerate(branch_id=branch, items=[
                {"variant_id": variants[0], "quantity": 1}]), client_id=clients[0])
        assert_payment_stock(stock_db, pending_payment_sale, status)


@pytest.mark.parametrize("final", ["COMPLETED", "DECLINED"])
def test_timeout_resolves_late_without_second_sale(stock_db, pending_payment_sale, final):
    engine, *_ = stock_db
    _, ref, _, _ = pending_payment_sale
    with Session(engine) as session:
        confirm_stock_payment(session, ref, "TIMEOUT")
        assert confirm_stock_payment(session, ref, "PENDING")["status"] == "TIMEOUT"
    assert_payment_stock(stock_db, pending_payment_sale, "TIMEOUT")
    with Session(engine) as session:
        confirm_stock_payment(session, ref, final)
        confirm_stock_payment(session, ref, final)
    assert_payment_stock(stock_db, pending_payment_sale, final)


@pytest.mark.parametrize("status", ["COMPLETED", "DECLINED", "TIMEOUT"])
def test_initial_gateway_status_is_reconciled(stock_db, pending_payment_sale, status):
    engine, *_ = stock_db
    _, ref, _, _ = pending_payment_sale
    with Session(engine) as session:
        session.query(Payment).filter_by(gateway_reference=ref).one().status = status
        session.commit()
        confirm_stock_payment(session, ref, status)
        confirm_stock_payment(session, ref, status)
    assert_payment_stock(stock_db, pending_payment_sale, status)


def test_declined_cannot_be_resurrected(stock_db, pending_payment_sale):
    engine, *_ = stock_db
    sale_id, ref, _, _ = pending_payment_sale
    with Session(engine) as session:
        confirm_stock_payment(session, ref, "DECLINED")
        assert confirm_stock_payment(session, ref, "COMPLETED")["status"] == "DECLINED"
        session.add(Payment(sale_id=sale_id, gateway_reference="late", amount=25,
                            method="mock", status="PENDING"))
        session.commit()
        with pytest.raises(ConflictError):
            confirm_stock_payment(session, "late", "COMPLETED")
        assert session.query(Payment).filter_by(gateway_reference="late").one().status == "PENDING"
    assert_payment_stock(stock_db, pending_payment_sale, "DECLINED")


def test_concurrent_declines_restore_once(stock_db, pending_payment_sale):
    _, ref, _, _ = pending_payment_sale
    assert compete(stock_db,
        lambda session: confirm_stock_payment(session, ref, "DECLINED"),
        lambda session: confirm_stock_payment(session, ref, "DECLINED"),
    ) == ("ok", "ok")
    assert_payment_stock(stock_db, pending_payment_sale, "DECLINED")


def test_receipt_failure_rolls_back_confirmation(stock_db, pending_payment_sale, monkeypatch):
    from app.services.receipt_service import receipt_service

    engine, *_ = stock_db
    _, ref, _, _ = pending_payment_sale
    def fail(*args, **kwargs):
        raise RuntimeError("receipt failure")
    monkeypatch.setattr(receipt_service, "generate", fail)
    with Session(engine) as session, pytest.raises(RuntimeError, match="receipt failure"):
        confirm_stock_payment(session, ref, "COMPLETED")
    assert_payment_stock(stock_db, pending_payment_sale, "PENDING")


def test_stock_restoration_failure_rolls_back_everything(stock_db, pending_payment_sale, monkeypatch):
    engine, *_ = stock_db
    _, ref, _, _ = pending_payment_sale
    original = sales_service.reject_pending_sale
    def fail_after_restoration(*args, **kwargs):
        original(*args, **kwargs)
        raise RuntimeError("restoration failure")
    monkeypatch.setattr(sales_service, "reject_pending_sale", fail_after_restoration)
    with Session(engine) as session, pytest.raises(RuntimeError, match="restoration failure"):
        confirm_stock_payment(session, ref, "DECLINED")
    assert_payment_stock(stock_db, pending_payment_sale, "PENDING")


def test_another_declined_reference_does_not_cancel_paid_sale(stock_db, pending_payment_sale):
    engine, *_ = stock_db
    sale_id, ref, _, _ = pending_payment_sale
    with Session(engine) as session:
        confirm_stock_payment(session, ref, "COMPLETED")
        session.add(Payment(sale_id=sale_id, gateway_reference="other", amount=25,
                            method="mock", status="PENDING"))
        session.commit()
        confirm_stock_payment(session, "other", "DECLINED")
    assert_payment_stock(stock_db, pending_payment_sale, "COMPLETED")


def test_completed_reference_prevents_release_by_another_payment(stock_db, pending_payment_sale):
    engine, *_ = stock_db
    sale_id, ref, _, _ = pending_payment_sale
    with Session(engine) as session:
        session.add(Payment(sale_id=sale_id, gateway_reference="completed_at_start", amount=25,
                            method="mock", status="COMPLETED"))
        session.commit()
        with pytest.raises(ConflictError):
            confirm_stock_payment(session, ref, "DECLINED")
    assert_payment_stock(stock_db, pending_payment_sale, "PENDING")

"""
Tests for CU-33, CU-34, CU-35: Reportes y Auditoría
"""
import json
import uuid
import hmac
import hashlib
from decimal import Decimal
from datetime import UTC, datetime, timedelta

import pytest

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import create_access_token
from app.models.sales import Sale, SaleDetail, SaleStatus, SalePaymentStatus, Receipt
from app.models.inventory import Inventory
from app.models.reservation import Reservation, ReservationDetail, ReservationStatus
from app.models.catalog import Garment, GarmentVariant, Category, Size, Color
from app.models.inventory import Inventory
from app.models.reservation import Reservation, ReservationDetail, ReservationStatus
from app.models.user import Client, User, Role, UserRole, Branch
from app.models.analytics import AuditLog
from app.models.sales import Payment, Sale, SaleDetail, SaleStatus, SalePaymentStatus, Receipt
from app.models.user import Client, User, Role, UserRole, Branch
from app.models.catalog import Garment, GarmentVariant, Category, Size, Color
from app.models.inventory import Inventory

import pytest

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import create_access_token
from app.models.sales import Sale, SaleDetail, SaleStatus, SalePaymentStatus, Receipt
from app.models.inventory import Inventory
from app.models.reservation import Reservation, ReservationDetail, ReservationStatus
from app.models.catalog import Garment, GarmentVariant, Category, Size, Color
from app.models.inventory import Inventory
from app.models.reservation import Reservation, ReservationDetail, ReservationStatus
from app.models.user import Client, User, Role, UserRole, Branch
from app.models.analytics import AuditLog
from app.models.sales import Payment, Sale, SaleDetail, SaleStatus, SalePaymentStatus, Receipt
from app.models.user import Client, User, Role, UserRole, Branch
from app.models.catalog import Garment, GarmentVariant, Category, Size, Color
from app.models.inventory import Inventory
from app.models.analytics import AuditLog
from app.models.user import User, Role, UserRole

import pytest

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import create_access_token
from app.models.sales import Sale, SaleDetail, SaleStatus, SalePaymentStatus, Receipt
from app.models.inventory import Inventory
from app.models.reservation import Reservation, ReservationDetail, ReservationStatus
from app.models.catalog import Garment, GarmentVariant, Category, Size, Color
from app.models.inventory import Inventory
from app.models.reservation import Reservation, ReservationDetail, ReservationStatus
from app.models.user import Client, User, Role, UserRole, Branch
from app.models.analytics import AuditLog
from app.models.sales import Payment, Sale, SaleDetail, SaleStatus, SalePaymentStatus, Receipt
from app.models.user import Client, User, Role, UserRole, Branch
from app.models.catalog import Garment, GarmentVariant, Category, Size, Color
from app.models.inventory import Inventory


class TestCU33ReportesIndicadores:
    """Tests para CU-33: Reportes e Indicadores (KPIs)"""

    @pytest.fixture(autouse=True)
    def setup_test_data(self, monkeypatch):
        """Setup test data for each test."""
        monkeypatch.setattr(settings, "static_qr_webhook_secret", "test_secret_123")
        monkeypatch.setattr(settings, "payment_gateway", "static_qr")
        monkeypatch.setattr(settings, "static_qr_auto_complete_seconds", 2)  # Fast for tests
        monkeypatch.setattr(settings, "static_qr_timeout_minutes", 10)
        monkeypatch.setattr(settings, "base_url_app", "http://localhost:8000")

    def _create_sale(self, total_amount=Decimal("150.00")):
        """Helper to create a test sale via direct DB."""
        db = SessionLocal()
        try:
            # Ensure branch exists
            branch = db.query(Branch).filter(Branch.id == 1).first()
            if not branch:
                branch = Branch(name="Sucursal Centro", address="Av. Principal 123", phone="123456789")
                db.add(branch)
                db.flush()

            # Ensure variant exists
            variant = db.query(GarmentVariant).filter(GarmentVariant.id == 1).first()
            if not variant:
                cat = Category(name="Test Category")
                db.add(cat)
                db.flush()
                g = Garment(name="Test Garment", base_price=Decimal("100"), category_id=cat.id, is_active=True)
                db.add(g)
                db.flush()
                size = Size(name="M")
                color = Color(name="Azul", hex_code="#0000FF")
                db.add_all([size, color])
                db.flush()
                variant = GarmentVariant(
                    garment_id=g.id,
                    sku="TEST-001",
                    price=Decimal("150.00"),
                    size_id=size.id,
                    color_id=color.id,
                )
                db.add(variant)
                db.flush()

            # Ensure inventory
            inv = db.query(Inventory).filter(Inventory.variant_id == 1, Inventory.branch_id == 1).first()
            if not inv:
                inv = Inventory(branch_id=1, variant_id=1, quantity=10, reserved_quantity=0)
                db.add(inv)

            # Create sale
            sale = Sale(
                invoice_number=f"TEST-{int(datetime.now(UTC).timestamp())}",
                branch_id=1,
                client_id=1,
                total_amount=Decimal("150.00"),
                payment_method="static_qr",
                status=SaleStatus.PAID,
                paid_at=datetime.now(UTC),
            )
            db.add(sale)
            db.commit()
            db.refresh(sale)
            return sale.id
        finally:
            db.close()
        return sale_id

    def _get_admin_token(self):
        """Get a valid admin token."""
        return create_access_token(subject="1", roles=["ADMIN"])

    def _get_admin_headers(self):
        """Get admin auth headers."""
        token = create_access_token(subject="1", roles=["ADMIN"])
        return {"Authorization": f"Bearer {token}"}

    def test_get_sales_indicators(self, client):
        """Test obtener indicadores de ventas."""
        # Create a sale first
        sale_id = self._create_sale(Decimal("150.00"))

        r = client.post(
            "/api/v1/reports/indicators",
            json={
                "start_date": (datetime.now(UTC) - timedelta(days=30)).isoformat(),
                "end_date": datetime.now(UTC).isoformat(),
                "branch_id": 1,
            },
            headers={"Authorization": f"Bearer {create_access_token(subject='1', roles=['ADMIN'])}"},
        )
        assert r.status_code == 200, r.text
        data = r.json()

        assert "generated_at" in data
        assert "period" in data
        assert "indicators" in data
        assert len(data["indicators"]) >= 4

        indicator_names = [ind["name"] for ind in data["indicators"]]
        assert "Ventas Totales" in indicator_names
        assert "Total Órdenes" in indicator_names
        assert "Ticket Promedio" in indicator_names

    def test_get_stock_indicators(self, client):
        """Test obtener indicadores de stock."""
        # Create inventory with low stock
        db = SessionLocal()
        try:
            inv = Inventory(branch_id=1, variant_id=1, quantity=5, reserved_quantity=0)
            db.add(inv)
            db.commit()
        finally:
            db.close()

        r = client.get(
            "/api/v1/reports/stock?branch_id=1&threshold=10",
            headers={"Authorization": f"Bearer {create_access_token(subject='1', roles=['ADMIN'])}"},
        )
        assert r.status_code == 200
        data = r.json()
        assert "generated_at" in data
        assert "items" in data
        assert "total_low_stock" in data
        assert "out_of_stock_count" in data


class TestCU34BitacoraTrazabilidad:
    """Tests para CU-34: Bitácora y Trazabilidad"""

    def _create_audit_log(self):
        """Helper to create a test audit log."""
        db = SessionLocal()
        try:
            log = AuditLog(
                user_id=1,
                action="CREATE",
                entity="Sale",
                entity_id=1,
                metadata_json='{"amount": 150.00}',
            )
            db.add(log)
            db.commit()
        finally:
            db.close()

    def test_get_audit_log(self, client):
        """Test obtener bitácora de auditoría."""
        db = SessionLocal()
        try:
            log = AuditLog(
                user_id=1,
                action="CREATE",
                entity="Sale",
                entity_id=1,
                metadata_json='{"amount": 150.00}',
            )
            db.add(log)
            db.commit()
        finally:
            db.close()

        r = client.get(
            "/api/v1/reports/audit-log?page=1&size=20",
            headers={"Authorization": f"Bearer {create_access_token(subject='1', roles=['ADMIN'])}"},
        )
        assert r.status_code == 200
        data = r.json()
        assert "items" in r.json()
        assert "total" in r.json()
        assert "page" in r.json()
        assert "size" in r.json()
        assert "pages" in r.json()

    def test_audit_log_filters(self, client):
        """Test filtros de bitácora."""
        db = SessionLocal()
        try:
            for i in range(3):
                log = AuditLog(
                    user_id=1,
                    action="CREATE" if i == 0 else "UPDATE" if i == 1 else "DELETE",
                    entity="Sale" if i % 2 == 0 else "Product",
                    entity_id=i + 1,
                    metadata_json='{"test": true}',
                )
                db.add(log)
            db.commit()
        finally:
            db.close()

        # Filtrar por acción
        r = client.get(
            "/api/v1/reports/audit-log?action=CREATE",
            headers={"Authorization": f"Bearer {create_access_token(subject='1', roles=['ADMIN'])}"},
        )
        assert r.status_code == 200
        data = r.json()
        assert all(item["action"] == "CREATE" for item in r.json()["items"])

        # Filtrar por entidad
        r = client.get("/api/v1/reports/audit-log?entity=Sale", headers={"Authorization": f"Bearer {create_access_token(subject='1', roles=['ADMIN'])}"})
        assert r.status_code == 200
        data = r.json()
        assert all(item["entity"] == "Sale" for item in r.json()["items"])


class TestCU35ConsolidadoVentasInventario:
    """Tests para CU-35: Información Consolidada"""

    def test_get_consolidated_report(self, client):
        """Test reporte consolidado de ventas e inventario."""
        r = client.get(
            "/api/v1/reports/consolidated",
            params={
                "start_date": (datetime.now(UTC) - timedelta(days=30)).isoformat(),
                "end_date": datetime.now(UTC).isoformat(),
                "branch_id": 1,
            },
            headers={"Authorization": f"Bearer {create_access_token(subject='1', roles=['ADMIN'])}"},
        )
        assert r.status_code == 200
        data = r.json()
        assert "generated_at" in data
        assert "period" in data
        assert "branches" in data
        assert "total_sales" in data
        assert "total_revenue" in data
        assert "total_orders" in data
        assert "total_stock" in data
        assert "low_stock_items" in data
        assert "top_selling_variant" in data
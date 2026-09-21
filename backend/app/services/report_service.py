"""
Report Service - Generación de reportes e indicadores.

CU-33: Indicadores de ventas y stock.
CU-35: Reporte consolidado de ventas e inventario.
CU-34: Bitácora de auditoría (delegado al AuditService).
"""
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import func, desc, case

from app.core.dependencies import DbSession
from app.models.inventory import Inventory
from app.models.catalog import GarmentVariant, Garment
from app.models.sales import Sale, SaleDetail, SaleStatus
from app.models.user import Branch
from app.models.analytics import AuditLog


class ReportService:
    """Servicio de reportes.

    Todos los métodos requieren autenticación de administrador
    (verificado en la capa de rutas).
    """

    def __init__(self, db: DbSession):
        self.db = db

    # ------------------------------------------------------------------
    # CU-33: Indicadores de ventas
    # ------------------------------------------------------------------
    def get_sales_indicators(self, start_date: datetime, end_date: datetime, branch_id: Optional[int] = None) -> dict:
        """Obtener indicadores de ventas para el período."""
        q = self.db.query(Sale).filter(
            Sale.status == SaleStatus.PAID,
            Sale.paid_at.isnot(None),
            Sale.paid_at >= start_date,
            Sale.paid_at <= end_date,
        )
        if branch_id:
            q = q.filter(Sale.branch_id == branch_id)

        total_orders = q.count()
        total_revenue = (
            self.db.query(func.coalesce(func.sum(Sale.total_amount), 0))
            .filter(
                Sale.status == SaleStatus.PAID,
                Sale.paid_at.isnot(None),
                Sale.paid_at >= start_date,
                Sale.paid_at <= end_date,
            )
            .filter(*([Sale.branch_id == branch_id] if branch_id else []))
            .scalar()
            or Decimal("0")
        )
        total_revenue = Decimal(total_revenue)
        avg_ticket = (
            Decimal(total_revenue) / Decimal(total_orders)
            if total_orders
            else Decimal("0")
        )

        units_q = (
            self.db.query(func.coalesce(func.sum(SaleDetail.quantity), 0))
            .join(Sale, SaleDetail.sale_id == Sale.id)
            .filter(
                Sale.status == SaleStatus.PAID,
                Sale.paid_at.isnot(None),
                Sale.paid_at >= start_date,
                Sale.paid_at <= end_date,
            )
        )
        if branch_id:
            units_q = units_q.filter(Sale.branch_id == branch_id)
        units_sold = units_q.scalar() or 0

        indicators = [
            {
                "name": "Ventas Totales",
                "value": total_revenue,
                "unit": "GTQ",
                "trend": None,
            },
            {
                "name": "Total Órdenes",
                "value": total_orders,
                "unit": "Órdenes",
                "trend": None,
            },
            {
                "name": "Ticket Promedio",
                "value": avg_ticket,
                "unit": "GTQ",
                "trend": None,
            },
            {
                "name": "Unidades Vendidas",
                "value": units_sold,
                "unit": "Unidades",
                "trend": None,
            },
        ]

        return {
            "generated_at": datetime.now(UTC),
            "period": f"{start_date.date().isoformat()} a {end_date.date().isoformat()}",
            "indicators": indicators,
        }

    # ------------------------------------------------------------------
    # CU-33: Indicadores de stock
    # ------------------------------------------------------------------
    def get_stock_indicators(self, branch_id: Optional[int] = None, threshold: int = 10) -> dict:
        """Obtener indicadores de stock bajo y agotado."""
        q = self.db.query(Inventory)
        if branch_id:
            q = q.filter(Inventory.branch_id == branch_id)

        items = []
        total_low_stock = 0
        out_of_stock_count = 0

        for inv in q.all():
            variant = inv.variant
            garment = variant.garment if variant else None
            available = getattr(inv, "available", inv.quantity - inv.reserved_quantity)
            out_of_stock = available <= 0
            low_stock = available < threshold

            if not (low_stock or out_of_stock):
                continue

            if out_of_stock:
                out_of_stock_count += 1
            else:
                total_low_stock += 1

            items.append(
                {
                    "branch_id": inv.branch_id,
                    "branch_name": self._branch_name(inv.branch_id),
                    "variant_id": inv.variant_id,
                    "variant_sku": variant.sku if variant else "",
                    "garment_name": garment.name if garment else "Desconocido",
                    "size_name": None,
                    "color_name": None,
                    "available": available,
                    "reserved_quantity": inv.reserved_quantity,
                    "out_of_stock": out_of_stock,
                    "status": "out_of_stock" if out_of_stock else "low",
                }
            )

        return {
            "generated_at": datetime.now(UTC),
            "items": items,
            "total_low_stock": total_low_stock,
            "out_of_stock_count": out_of_stock_count,
        }

    # ------------------------------------------------------------------
    # CU-33: Ventas por período
    # ------------------------------------------------------------------
    def get_sales_by_period(
        self,
        period_type: str = "daily",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        branch_id: Optional[int] = None,
    ) -> dict:
        """Obtener ventas agrupadas por período."""
        q = self.db.query(
            Sale.branch_id,
            Sale.paid_at,
            Sale.total_amount,
        ).filter(
            Sale.status == SaleStatus.PAID,
            Sale.paid_at.isnot(None),
        )
        if start_date:
            q = q.filter(Sale.paid_at >= start_date)
        if end_date:
            q = q.filter(Sale.paid_at <= end_date)
        if branch_id:
            q = q.filter(Sale.branch_id == branch_id)

        buckets = {}
        for _, paid_at, amount in q.all():
            if period_type == "monthly":
                key = paid_at.strftime("%Y-%m")
            elif period_type == "weekly":
                key = paid_at.strftime("%Y-W%W")
            else:
                key = paid_at.strftime("%Y-%m-%d")
            bucket = buckets.setdefault(key, {"sales": Decimal("0"), "orders": 0})
            bucket["sales"] += amount or Decimal("0")
            bucket["orders"] += 1

        data = []
        for key in sorted(buckets):
            bucket = buckets[key]
            data.append(
                {
                    "period": key,
                    "total_sales": bucket["sales"],
                    "order_count": bucket["orders"],
                    "avg_ticket": (
                        bucket["sales"] / Decimal(bucket["orders"])
                        if bucket["orders"]
                        else Decimal("0")
                    ),
                }
            )

        return {
            "generated_at": datetime.now(UTC),
            "period_type": period_type,
            "data": data,
        }

    # ------------------------------------------------------------------
    # CU-33: Top productos
    # ------------------------------------------------------------------
    def get_top_products(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 10,
        branch_id: Optional[int] = None,
    ) -> dict:
        """Obtener productos más vendidos."""
        q = (
            self.db.query(
                SaleDetail.variant_id,
                func.sum(SaleDetail.quantity).label("total_qty"),
                func.sum(SaleDetail.quantity * SaleDetail.unit_price).label("total_rev"),
            )
            .join(Sale, SaleDetail.sale_id == Sale.id)
            .filter(
                Sale.status == SaleStatus.PAID,
                Sale.paid_at.isnot(None),
                Sale.paid_at >= start_date,
                Sale.paid_at <= end_date,
            )
            .group_by(SaleDetail.variant_id)
            .order_by(desc(func.sum(SaleDetail.quantity)))
            .limit(limit)
        )
        if branch_id:
            q = q.filter(Sale.branch_id == branch_id)

        items = []
        for variant_id, total_qty, total_rev in q.all():
            variant = (
                self.db.query(GarmentVariant)
                .filter(GarmentVariant.id == variant_id)
                .first()
            )
            garment = variant.garment if variant else None
            items.append(
                {
                    "variant_id": variant_id,
                    "garment_name": garment.name if garment else "Desconocido",
                    "variant_sku": variant.sku if variant else "",
                    "total_quantity": int(total_qty or 0),
                    "total_revenue": total_rev or Decimal("0"),
                    "avg_price": (
                        (total_rev or Decimal("0")) / Decimal(total_qty)
                        if total_qty
                        else Decimal("0")
                    ),
                }
            )

        return {
            "generated_at": datetime.now(UTC),
            "period": f"{start_date.date().isoformat()} a {end_date.date().isoformat()}",
            "items": items,
        }

    # ------------------------------------------------------------------
    # CU-33: Productos con stock bajo
    # ------------------------------------------------------------------
    def get_low_stock(self, branch_id: Optional[int] = None, threshold: int = 10) -> dict:
        """Obtener productos con stock bajo o agotado."""
        return self.get_stock_indicators(branch_id, threshold)

    # ------------------------------------------------------------------
    # CU-33: Rotación de inventario
    # ------------------------------------------------------------------
    def get_inventory_turnover(
        self,
        start_date: datetime,
        end_date: datetime,
        branch_id: Optional[int] = None,
    ) -> dict:
        """Obtener rotación de inventario por variante."""
        q = self.db.query(Inventory)
        if branch_id:
            q = q.filter(Inventory.branch_id == branch_id)

        items = []
        for inv in q.all():
            variant = inv.variant
            garment = variant.garment if variant else None
            available = getattr(inv, "available", inv.quantity - inv.reserved_quantity)
            avg_sales = self._avg_daily_sales(inv.variant_id, start_date, end_date, branch_id)
            days_of_stock = (available / avg_sales) if avg_sales > 0 else None
            items.append(
                {
                    "branch_id": inv.branch_id,
                    "branch_name": self._branch_name(inv.branch_id),
                    "variant_id": inv.variant_id,
                    "variant_sku": variant.sku if variant else "",
                    "garment_name": garment.name if garment else "Desconocido",
                    "avg_daily_sales": avg_sales,
                    "current_stock": available,
                    "days_of_stock": days_of_stock,
                    "turnover_rate": None,
                }
            )

        return {
            "generated_at": datetime.now(UTC),
            "period": f"{start_date.date().isoformat()} a {end_date.date().isoformat()}",
            "items": items,
        }

    def _avg_daily_sales(self, variant_id, start_date, end_date, branch_id):
        q = (
            self.db.query(func.coalesce(func.sum(SaleDetail.quantity), 0))
            .join(Sale, SaleDetail.sale_id == Sale.id)
            .filter(
                SaleDetail.variant_id == variant_id,
                Sale.status == SaleStatus.PAID,
                Sale.paid_at.isnot(None),
                Sale.paid_at >= start_date,
                Sale.paid_at <= end_date,
            )
        )
        if branch_id:
            q = q.filter(Sale.branch_id == branch_id)
        total = q.scalar() or 0
        days = max((end_date - start_date).days, 1)
        return Decimal(total) / Decimal(days)

    # ------------------------------------------------------------------
    # CU-35: Reporte consolidado
    # ------------------------------------------------------------------
    def get_consolidated_report(
        self,
        start_date: datetime,
        end_date: datetime,
        branch_id: Optional[int] = None,
    ) -> dict:
        """Obtener reporte consolidado de ventas e inventario."""
        sales_q = (
            self.db.query(Sale)
            .filter(
                Sale.status == SaleStatus.PAID,
                Sale.paid_at.isnot(None),
                Sale.paid_at >= start_date,
                Sale.paid_at <= end_date,
            )
        )
        if branch_id:
            sales_q = sales_q.filter(Sale.branch_id == branch_id)

        total_sales = sales_q.count()
        total_revenue = (
            self.db.query(func.coalesce(func.sum(Sale.total_amount), 0))
            .filter(
                Sale.status == SaleStatus.PAID,
                Sale.paid_at.isnot(None),
                Sale.paid_at >= start_date,
                Sale.paid_at <= end_date,
            )
            .filter(*([Sale.branch_id == branch_id] if branch_id else []))
            .scalar()
            or Decimal("0")
        )
        total_revenue = Decimal(total_revenue)

        branches = self._branch_summary(start_date, end_date, branch_id)
        top_variant = self._top_selling_variant(start_date, end_date, branch_id)

        return {
            "generated_at": datetime.now(UTC),
            "period": f"{start_date.date().isoformat()} a {end_date.date().isoformat()}",
            "branches": branches,
            "total_sales": total_sales,
            "total_revenue": total_revenue,
            "total_orders": total_sales,
            "total_stock": self._total_stock(branch_id),
            "low_stock_items": self._count_low_stock(branch_id),
            "top_selling_variant": top_variant,
        }

    def _branch_summary(self, start_date, end_date, branch_id):
        q = (
            self.db.query(
                Sale.branch_id,
                func.count(Sale.id).label("orders"),
                func.coalesce(func.sum(Sale.total_amount), 0).label("revenue"),
            )
            .filter(
                Sale.status == SaleStatus.PAID,
                Sale.paid_at.isnot(None),
                Sale.paid_at >= start_date,
                Sale.paid_at <= end_date,
            )
            .group_by(Sale.branch_id)
        )
        if branch_id:
            q = q.filter(Sale.branch_id == branch_id)

        rows = []
        for bid, orders, revenue in q.all():
            rows.append(
                {
                    "branch_id": bid,
                    "branch_name": self._branch_name(bid),
                    "total_sales": self._branch_sales_units(start_date, end_date, bid),
                    "total_orders": int(orders),
                    "total_revenue": Decimal(revenue),
                    "total_stock": self._total_stock(bid),
                    "low_stock_items": self._count_low_stock(bid),
                }
            )
        return rows

    def _branch_sales_units(self, start_date, end_date, branch_id):
        q = (
            self.db.query(func.coalesce(func.sum(SaleDetail.quantity), 0))
            .join(Sale, SaleDetail.sale_id == Sale.id)
            .filter(
                Sale.status == SaleStatus.PAID,
                Sale.paid_at.isnot(None),
                Sale.paid_at >= start_date,
                Sale.paid_at <= end_date,
            )
        )
        if branch_id:
            q = q.filter(Sale.branch_id == branch_id)
        return int(q.scalar() or 0)

    def _branch_name(self, branch_id):
        try:
            branch = (
                self.db.query(Branch).filter(Branch.id == branch_id).first()
            )
            return branch.name if branch else f"Sucursal {branch_id}"
        except Exception:
            return f"Sucursal {branch_id}"

    def _top_selling_variant(self, start_date, end_date, branch_id):
        q = (
            self.db.query(
                SaleDetail.variant_id,
                func.sum(SaleDetail.quantity).label("qty"),
            )
            .join(Sale, SaleDetail.sale_id == Sale.id)
            .filter(
                Sale.status == SaleStatus.PAID,
                Sale.paid_at.isnot(None),
                Sale.paid_at >= start_date,
                Sale.paid_at <= end_date,
            )
        )
        if branch_id:
            q = q.filter(Sale.branch_id == branch_id)
        q = (
            q.group_by(SaleDetail.variant_id)
            .order_by(desc(func.sum(SaleDetail.quantity)))
            .limit(1)
        )
        row = q.first()
        if not row:
            return None
        variant = (
            self.db.query(GarmentVariant)
            .filter(GarmentVariant.id == row.variant_id)
            .first()
        )
        return {
            "variant_id": row.variant_id,
            "variant_sku": variant.sku if variant else "",
            "garment_name": variant.garment.name if variant and variant.garment else "Desconocido",
            "total_quantity": int(row.qty or 0),
        }

    def _total_stock(self, branch_id):
        q = self.db.query(func.coalesce(func.sum(Inventory.quantity), 0))
        if branch_id:
            q = q.filter(Inventory.branch_id == branch_id)
        return int(q.scalar() or 0)

    def _count_low_stock(self, branch_id):
        q = self.db.query(Inventory)
        if branch_id:
            q = q.filter(Inventory.branch_id == branch_id)
        return sum(
            1
            for inv in q.all()
            if getattr(inv, "available", inv.quantity - inv.reserved_quantity) < 10
        )


def get_report_service(db: DbSession) -> ReportService:
    """Factory para obtener una instancia del servicio de reportes."""
    return ReportService(db)

from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel

from app.schemas.common import ORMModel


class IndicatorType(str, Enum):
    SALES_TOTAL = "sales_total"
    SALES_COUNT = "sales_count"
    AVERAGE_TICKET = "average_ticket"
    STOCK_TOTAL = "stock_total"
    STOCK_LOW = "stock_low"
    STOCK_OUT = "stock_out"
    INVENTORY_TURNOVER = "inventory_turnover"
    TOP_PRODUCTS = "top_products"
    TOP_CATEGORIES = "top_categories"
    SALES_BY_BRANCH = "sales_by_branch"
    SALES_BY_CATEGORY = "sales_by_category"
    SALES_BY_PERIOD = "sales_by_period"
    LOW_STOCK_ALERTS = "low_stock_alerts"


class IndicatorsRequest(BaseModel):
    start_date: datetime
    end_date: datetime
    branch_id: int | None = None
    indicator_types: list[IndicatorType] | None = None


class IndicatorItem(BaseModel):
    name: str
    value: float | int
    unit: str | None = None
    trend: float | None = None  # percentage change vs previous period


class IndicatorsResponse(ORMModel):
    generated_at: datetime
    period: str
    indicators: list[IndicatorItem]


class AuditLogItem(ORMModel):
    id: int
    user_id: int | None = None
    user_email: str | None = None
    action: str
    entity: str | None = None
    entity_id: int | None = None
    metadata_json: str | None = None
    created_at: datetime


class AuditLogPageResponse(ORMModel):
    items: list[AuditLogItem]
    total: int
    page: int
    size: int
    pages: int


class ConsolidatedItem(BaseModel):
    branch_id: int
    branch_name: str
    total_sales: Decimal
    total_orders: int
    total_revenue: Decimal
    total_stock: int
    low_stock_items: int
    top_selling_variant: str | None = None


class ConsolidatedResponse(ORMModel):
    generated_at: datetime
    period: str
    branches: list[ConsolidatedItem]
    total_sales: Decimal
    total_revenue: Decimal
    total_orders: int
    total_stock: int
    low_stock_items: int
    top_selling_variant: dict | None = None


class SalesByPeriodItem(BaseModel):
    period: str  # YYYY-MM or YYYY-MM-DD
    total_sales: Decimal
    order_count: int
    avg_ticket: Decimal


class SalesByPeriodResponse(ORMModel):
    generated_at: datetime
    period_type: str  # daily, weekly, monthly
    data: list[SalesByPeriodItem]


class TopProductsItem(BaseModel):
    variant_id: int
    garment_name: str
    variant_sku: str
    size_name: str | None = None
    color_name: str | None = None
    total_quantity: int
    total_revenue: Decimal
    avg_price: Decimal


class TopProductsResponse(ORMModel):
    generated_at: datetime
    period: str
    items: list[TopProductsItem]


class LowStockItem(BaseModel):
    branch_id: int
    branch_name: str
    variant_id: int
    variant_sku: str
    garment_name: str
    size_name: str | None = None
    color_name: str | None = None
    available: int
    reserved_quantity: int


class LowStockResponse(ORMModel):
    generated_at: datetime
    items: list[dict]
    total_low_stock: int
    out_of_stock_count: int


class TopCategoriesItem(BaseModel):
    category_id: int
    category_name: str
    total_revenue: Decimal
    total_quantity: int
    avg_price: Decimal
    margin_pct: Decimal | None = None


class TopCategoriesResponse(ORMModel):
    generated_at: datetime
    period: str
    items: list[TopCategoriesItem]


class InventoryTurnoverItem(BaseModel):
    branch_id: int
    branch_name: str
    variant_id: int
    variant_sku: str
    garment_name: str
    avg_daily_sales: Decimal
    current_stock: int
    days_of_stock: Decimal | None = None
    turnover_rate: Decimal | None = None


class InventoryTurnoverResponse(ORMModel):
    generated_at: datetime
    period: str
    items: list[InventoryTurnoverItem]
    avg_turnover_rate: Decimal


class TopCategoriesItem(BaseModel):
    category_id: int
    category_name: str
    total_revenue: Decimal
    total_quantity: int
    avg_price: Decimal
    margin_pct: Decimal | None = None


class TopCategoriesResponse(ORMModel):
    generated_at: datetime
    period: str
    items: list[TopCategoriesItem]


class InventoryValuationItem(BaseModel):
    branch_id: int
    branch_name: str
    variant_id: int
    variant_sku: str
    garment_name: str
    quantity: int
    unit_cost: Decimal
    total_value: Decimal


class InventoryValuationResponse(ORMModel):
    generated_at: datetime
    items: list[InventoryValuationItem]
    total_value: Decimal
    total_items: int

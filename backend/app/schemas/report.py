from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, Field

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
    branch_id: Optional[int] = None
    indicator_types: Optional[List[IndicatorType]] = None


class IndicatorItem(BaseModel):
    name: str
    value: float | int
    unit: Optional[str] = None
    trend: Optional[float] = None  # percentage change vs previous period


class IndicatorsResponse(ORMModel):
    generated_at: datetime
    period: str
    indicators: List[IndicatorItem]


class AuditLogItem(ORMModel):
    id: int
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    action: str
    entity: Optional[str] = None
    entity_id: Optional[int] = None
    metadata_json: Optional[str] = None
    created_at: datetime


class AuditLogPageResponse(ORMModel):
    items: List[AuditLogItem]
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
    top_selling_variant: Optional[str] = None


class ConsolidatedResponse(ORMModel):
    generated_at: datetime
    period: str
    branches: List[ConsolidatedItem]
    total_sales: Decimal
    total_revenue: Decimal
    total_orders: int
    total_stock: int
    low_stock_items: int
    top_selling_variant: Optional[dict] = None


class SalesByPeriodItem(BaseModel):
    period: str  # YYYY-MM or YYYY-MM-DD
    total_sales: Decimal
    order_count: int
    avg_ticket: Decimal


class SalesByPeriodResponse(ORMModel):
    generated_at: datetime
    period_type: str  # daily, weekly, monthly
    data: List[SalesByPeriodItem]


class TopProductsItem(BaseModel):
    variant_id: int
    garment_name: str
    variant_sku: str
    size_name: Optional[str] = None
    color_name: Optional[str] = None
    total_quantity: int
    total_revenue: Decimal
    avg_price: Decimal


class TopProductsResponse(ORMModel):
    generated_at: datetime
    period: str
    items: List[TopProductsItem]


class LowStockItem(BaseModel):
    branch_id: int
    branch_name: str
    variant_id: int
    variant_sku: str
    garment_name: str
    size_name: Optional[str] = None
    color_name: Optional[str] = None
    available: int
    reserved_quantity: int


class LowStockResponse(ORMModel):
    generated_at: datetime
    items: List[dict]
    total_low_stock: int
    out_of_stock_count: int


class TopCategoriesItem(BaseModel):
    category_id: int
    category_name: str
    total_revenue: Decimal
    total_quantity: int
    avg_price: Decimal
    margin_pct: Optional[Decimal] = None


class TopCategoriesResponse(ORMModel):
    generated_at: datetime
    period: str
    items: List[TopCategoriesItem]


class InventoryTurnoverItem(BaseModel):
    branch_id: int
    branch_name: str
    variant_id: int
    variant_sku: str
    garment_name: str
    avg_daily_sales: Decimal
    current_stock: int
    days_of_stock: Optional[Decimal] = None
    turnover_rate: Optional[Decimal] = None


class InventoryTurnoverResponse(ORMModel):
    generated_at: datetime
    period: str
    items: List[InventoryTurnoverItem]
    avg_turnover_rate: Decimal


class TopCategoriesItem(BaseModel):
    category_id: int
    category_name: str
    total_revenue: Decimal
    total_quantity: int
    avg_price: Decimal
    margin_pct: Optional[Decimal] = None


class TopCategoriesResponse(ORMModel):
    generated_at: datetime
    period: str
    items: List[TopCategoriesItem]


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
    items: List[InventoryValuationItem]
    total_value: Decimal
    total_items: int
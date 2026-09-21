from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class IndicatorItem(BaseModel):
    name: str
    value: float | int
    unit: Optional[str] = None
    trend: Optional[float] = None  # percentage change vs previous period


class IndicatorsResponse(ORMModel):
    generated_at: datetime
    period: str
    indicators: List[dict]


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
    items: List[dict]
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
    branches: List[dict]
    total_sales: Decimal
    total_revenue: Decimal
    total_orders: int
    total_stock: int
    low_stock_items: int


class InventoryStatusItem(BaseModel):
    branch_id: int
    branch_name: str
    variant_id: int
    variant_sku: str
    garment_name: str
    size_name: Optional[str] = None
    color_name: Optional[str] = None
    quantity: int
    reserved_quantity: int
    available: int
    is_low_stock: bool


class StockStatusResponse(ORMModel):
    generated_at: datetime
    items: List[dict]
    total_items: int
    low_stock_count: int
    out_of_stock_count: int


class SalesByPeriodItem(BaseModel):
    period: str  # YYYY-MM or YYYY-MM-DD
    total_sales: Decimal
    order_count: int
    avg_ticket: Decimal


class SalesByPeriodResponse(ORMModel):
    generated_at: datetime
    period_type: str  # daily, weekly, monthly
    data: List[dict]


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
    items: List[dict]


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


class TopCustomersItem(BaseModel):
    client_id: int
    client_name: str
    client_email: str
    total_orders: int
    total_spent: Decimal
    avg_ticket: Decimal
    last_purchase: Optional[datetime] = None


class TopCustomersResponse(ORMModel):
    generated_at: datetime
    period: str
    items: List[dict]


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
    items: List[dict]
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
    items: List[dict]


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
    items: List[dict]
    total_value: Decimal
    total_items: int
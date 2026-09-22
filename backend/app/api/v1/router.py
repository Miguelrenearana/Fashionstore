from fastapi import APIRouter

from app.api.v1.routes_ai import router as ai_router
from app.api.v1.routes_auth import router as auth_router
from app.api.v1.routes_cart import router as cart_router
from app.api.v1.routes_catalog import router as catalog_router
from app.api.v1.routes_catalog_config import router as catalog_config_router
from app.api.v1.routes_clients import router as clients_router
from app.api.v1.routes_history import router as history_router
from app.api.v1.routes_inventory import router as inventory_router
from app.api.v1.routes_locations import router as locations_router
from app.api.v1.routes_notifications import router as notifications_router
from app.api.v1.routes_products import router as products_router
from app.api.v1.routes_promotions import router as promotions_router
from app.api.v1.routes_receipt import router as receipt_router
from app.api.v1.routes_reception import router as reception_router
from app.api.v1.routes_recommendations import router as recommendations_router
from app.api.v1.routes_reports import router as reports_router
from app.api.v1.routes_reservations import router as reservations_router
from app.api.v1.routes_sales import router as sales_router
from app.api.v1.routes_suppliers import router as suppliers_router
from app.api.v1.routes_users import router as users_router
from app.payments.api.v1.payments import router as payments_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(clients_router)
api_router.include_router(locations_router)
api_router.include_router(catalog_router)
api_router.include_router(catalog_config_router)
api_router.include_router(products_router)
api_router.include_router(promotions_router)
api_router.include_router(receipt_router)
api_router.include_router(history_router)
api_router.include_router(inventory_router)
api_router.include_router(reservations_router)
api_router.include_router(cart_router)
api_router.include_router(sales_router)
api_router.include_router(reception_router)
api_router.include_router(recommendations_router)
api_router.include_router(notifications_router)
api_router.include_router(suppliers_router)
api_router.include_router(ai_router)
api_router.include_router(reports_router)
api_router.include_router(payments_router)

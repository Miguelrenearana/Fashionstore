from fastapi import APIRouter

from app.core.dependencies import CurrentUser, DbSession
from app.core.exceptions import NotFoundError
from app.models.user import Client
from app.schemas.cart import CartCheckout, CartItemIn, CartRead
from app.services.cart_service import cart_service

router = APIRouter(prefix="/cart", tags=["cart"])


def _client_id(db, user) -> int:
    client = db.query(Client).filter(Client.user_id == user.id).first()
    if not client:
        raise NotFoundError("Client profile not found for user.")
    return client.id


@router.get("", response_model=CartRead)
def get_cart(db: DbSession, current: CurrentUser):
    client_id = _client_id(db, current)
    cart = cart_service.get_or_create(db, client_id)
    return cart


@router.post("/items", response_model=CartRead)
def add_item(db: DbSession, payload: CartItemIn, current: CurrentUser):
    client_id = _client_id(db, current)
    cart = cart_service.get_or_create(db, client_id)
    return cart_service.add_item(db, cart, payload.variant_id, payload.quantity)


@router.post("/checkout")
def checkout(db: DbSession, payload: CartCheckout, current: CurrentUser):
    client_id = _client_id(db, current)
    cart = cart_service.get_or_create(db, client_id, payload.branch_id)
    return {
        "cart_id": cart.id,
        "total": cart.total,
        "payment_gateway": payload.payment_gateway,
        "message": "Checkout intent created.",
    }

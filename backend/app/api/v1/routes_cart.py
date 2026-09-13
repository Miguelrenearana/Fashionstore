from fastapi import APIRouter

from app.core.dependencies import CurrentUser, DbSession
from app.core.exceptions import NotFoundError, ValidationError
from app.models.user import Client
from app.schemas.cart import CartCheckout, CartItemIn, CartRead
from app.schemas.reservation import ReservationCreate, ReservationItem, ReservationRead
from app.services.cart_service import cart_service
from app.services.reservation_service import reservation_service

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


@router.post("/checkout", response_model=ReservationRead)
def checkout(db: DbSession, payload: CartCheckout, current: CurrentUser):
    client_id = _client_id(db, current)
    cart = cart_service.get_or_create(
        db, client_id, payload.branch_id or None
    )
    if not cart.details:
        raise ValidationError("Cart is empty, cannot checkout.")
    items = [
        ReservationItem(variant_id=d.variant_id, quantity=d.quantity) for d in cart.details
    ]
    reservation = reservation_service.create(
        db,
        client_id,
        ReservationCreate(
            branch_id=payload.branch_id or cart.branch_id,
            items=items,
            notes="Checkout desde el carrito",
        ),
    )
    cart_service.clear(db, cart)
    return reservation

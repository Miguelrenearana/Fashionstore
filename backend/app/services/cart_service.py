from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationError
from app.models.cart import Cart, CartDetail
from app.models.inventory import Inventory


class CartService:
    def get_or_create(self, db: Session, client_id: int, branch_id: int | None = None) -> Cart:
        cart = db.query(Cart).filter(Cart.client_id == client_id, Cart.is_active).first()
        if not cart:
            cart = Cart(client_id=client_id, branch_id=branch_id)
            db.add(cart)
            db.commit()
            db.refresh(cart)
        return cart

    def add_item(self, db: Session, cart: Cart, variant_id: int, quantity: int) -> Cart:
        if quantity <= 0:
            raise ValidationError("Quantity must be positive.")
        detail = next((d for d in cart.details if d.variant_id == variant_id), None)
        if detail:
            detail.quantity += quantity
        else:
            inventory = self._find_inventory(db, cart, variant_id)
            if not inventory:
                raise NotFoundError("Variant not available in any branch.")
            unit_price = inventory.variant.price if inventory.variant else 0
            detail = CartDetail(
                cart=cart,
                variant_id=variant_id,
                quantity=quantity,
                unit_price=unit_price,
            )
            db.add(detail)
        db.commit()
        db.refresh(cart)
        return cart

    @staticmethod
    def _find_inventory(db: Session, cart: Cart, variant_id: int) -> Inventory | None:
        query = db.query(Inventory).filter(Inventory.variant_id == variant_id)
        if cart.branch_id:
            inventory = query.filter(Inventory.branch_id == cart.branch_id).first()
            if inventory:
                return inventory
            return None
        inventory = query.filter(Inventory.quantity > 0).order_by(Inventory.id).first()
        if inventory:
            cart.branch_id = inventory.branch_id
            return inventory
        return None

    def clear(self, db: Session, cart: Cart) -> None:
        for detail in list(cart.details):
            db.delete(detail)
        cart.is_active = False
        db.commit()


cart_service = CartService()

from collections.abc import Iterable
from contextlib import contextmanager

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from app.models.inventory import Inventory


@contextmanager
def stock_transaction(db: Session):
    """Keep stock and its business document in the same transaction."""
    try:
        yield
        db.commit()
    except Exception:
        db.rollback()
        raise


def lock_stock(
    db: Session, keys: Iterable[tuple[int, int]], *, create_missing: bool = False
) -> dict[tuple[int, int], Inventory]:
    """Lock (branch, variant) pairs in one global order, before any mutation.

    populate_existing refreshes objects already loaded by API serializers or
    authorization queries. Locks live until the caller commits or rolls back.
    The upsert also serializes concurrent creation of an absent inventory row.
    """
    rows = {}
    for branch_id, variant_id in sorted(set(keys)):
        if create_missing:
            insert = pg_insert if db.get_bind().dialect.name == "postgresql" else sqlite_insert
            db.execute(
                insert(Inventory).values(
                    branch_id=branch_id, variant_id=variant_id,
                    quantity=0, reserved_quantity=0,
                ).on_conflict_do_nothing(index_elements=["variant_id", "branch_id"])
            )
        row = (
            db.query(Inventory)
            .filter(Inventory.branch_id == branch_id, Inventory.variant_id == variant_id)
            .populate_existing()
            .with_for_update(of=Inventory)
            .one_or_none()
        )
        if row is not None:
            rows[branch_id, variant_id] = row
    return rows

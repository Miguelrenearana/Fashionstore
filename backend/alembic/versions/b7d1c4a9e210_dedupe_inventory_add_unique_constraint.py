"""dedupe inventory and add unique (variant_id, branch_id)

Revision ID: b7d1c4a9e210
Revises: 62fce272acff
Create Date: 2026-09-26

Motivo: la tabla `inventario` permitia varias filas para la misma pareja
(variant_id, branch_id). Eso duplicaba el stock agregado y hacia que CU-14
reportara existencias infladas. Se consolidate cada pareja en una fila y se
agrega la restriccion que lo impide.
"""
import sqlalchemy as sa
from alembic import op

revision = "b7d1c4a9e210"
down_revision = "62fce272acff"
branch_labels = None
depends_on = None

CONSTRAINT = "uq_inventario_variante_sucursal"


def upgrade() -> None:
    # Conserva la fila mas antigua de cada pareja y suma las demas.
    op.execute(
        """
        UPDATE inventario AS keeper
        SET quantity = sub.total_quantity,
            reserved_quantity = sub.total_reserved
        FROM (
            SELECT variant_id,
                   branch_id,
                   MIN(id) AS keep_id,
                   SUM(quantity) AS total_quantity,
                   SUM(reserved_quantity) AS total_reserved
            FROM inventario
            GROUP BY variant_id, branch_id
            HAVING COUNT(*) > 1
        ) AS sub
        WHERE keeper.variant_id = sub.variant_id
          AND keeper.branch_id = sub.branch_id
          AND keeper.id = sub.keep_id
        """
    )
    op.execute(
        """
        DELETE FROM inventario
        WHERE id NOT IN (
            SELECT MIN(id) FROM inventario GROUP BY variant_id, branch_id
        )
        """
    )
    op.create_unique_constraint(
        CONSTRAINT, "inventario", ["variant_id", "branch_id"]
    )


def downgrade() -> None:
    op.drop_constraint(CONSTRAINT, "inventario", type_="unique")

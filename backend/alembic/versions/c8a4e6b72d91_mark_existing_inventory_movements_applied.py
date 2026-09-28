"""Mark existing inventory movements as already reflected in stock.

Revision ID: c8a4e6b72d91
Revises: b7d1c4a9e210
"""

import sqlalchemy as sa

from alembic import op

revision = "c8a4e6b72d91"
down_revision = "b7d1c4a9e210"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Existing IN rows came from applied adjustments or demo history. There is
    # no marker that would identify an older, truly pending row reliably.
    op.add_column(
        "movimiento_inventario",
        sa.Column("is_applied", sa.Boolean(), nullable=False, server_default=sa.true()),
    )


def downgrade() -> None:
    op.drop_column("movimiento_inventario", "is_applied")

"""ciclo 2: password reset table

Revision ID: 0002_ci2_extra
Revises: 0001_initial
Create Date: 2026-09-13
"""
import sqlalchemy as sa

from alembic import op

revision = "0002_ci2_extra"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "password_reset",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(128), unique=True, nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_password_reset_user_id", "password_reset", ["user_id"])
    op.create_index("ix_password_reset_token_hash", "password_reset", ["token_hash"], unique=True)


def downgrade() -> None:
    op.drop_table("password_reset")

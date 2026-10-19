"""add user ban fields"""
from alembic import op
import sqlalchemy as sa

revision = "002_user_ban"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")))
    op.add_column("users", sa.Column("ban_reason", sa.String(255), nullable=True))


def downgrade():
    op.drop_column("users", "ban_reason")
    op.drop_column("users", "is_active")

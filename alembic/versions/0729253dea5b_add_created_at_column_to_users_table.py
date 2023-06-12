"""add created at column to Users table

Revision ID: 0729253dea5b
Revises: f56c0a1ee8a1
Create Date: 2023-06-12 14:40:09.738559

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0729253dea5b'
down_revision = 'f56c0a1ee8a1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=True, server_default=sa.func.now()))
    op.create_unique_constraint('email', 'users', ['email'])
    pass


def downgrade() -> None:
    op.drop_column('users', 'created_at')
    op.drop_constraint('email', 'users', type_='unique')
    pass

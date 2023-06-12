"""add more columns to post

Revision ID: 8e9c92b04aa5
Revises: 0729253dea5b
Create Date: 2023-06-12 14:56:38.193673

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8e9c92b04aa5'
down_revision = '0729253dea5b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('piblished', sa.Boolean(), nullable=False, server_default='True'))
    op.add_column('posts', sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()))
    pass


def downgrade() -> None:
    op.drop_column('posts', 'created_at')
    op.drop_column('posts', 'piblished')
    pass

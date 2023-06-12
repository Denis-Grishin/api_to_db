"""create cintent field in post table

Revision ID: f56c0a1ee8a1
Revises: 846cd92bf499
Create Date: 2023-06-12 14:34:28.024763

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f56c0a1ee8a1'
down_revision = '846cd92bf499'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('content', sa.String(length=100), nullable=True))
    pass


def downgrade() -> None:
    op.drop_column('posts', 'content')
    pass

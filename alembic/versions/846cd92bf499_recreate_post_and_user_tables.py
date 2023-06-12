"""recreate post and user tables

Revision ID: 846cd92bf499
Revises: 1793de0ad520
Create Date: 2023-06-12 14:32:48.757222

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '846cd92bf499'
down_revision = '1793de0ad520'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('users', sa.Column('id', sa.Integer(), nullable=False, primary_key=True), sa.Column('email', sa.String(length=100), nullable=False), sa.Column('password', sa.String(length=100), nullable=False), sa.PrimaryKeyConstraint('id'), sa.UniqueConstraint('email'))
    
    op.create_table('posts', sa.Column('id', sa.Integer(), nullable=False, primary_key=True), sa.Column('title', sa.String(length=100), nullable=False), sa.Column('owner_id', sa.Integer(), nullable=True), sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ), sa.PrimaryKeyConstraint('id'))
    pass


def downgrade() -> None:
    op.drop_table('posts')
    op.drop_table('users')
    pass

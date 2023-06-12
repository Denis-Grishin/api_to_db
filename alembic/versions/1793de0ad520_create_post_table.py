"""create post table

Revision ID: 1793de0ad520
Revises: 
Create Date: 2023-06-09 17:46:55.141153

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1793de0ad520'
down_revision = None
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

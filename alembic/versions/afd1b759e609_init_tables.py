"""init tables

Revision ID: afd1b759e609
Revises: 
Create Date: 2020-06-27 17:32:26.918946

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'afd1b759e609'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bookmarks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('command', sa.String(), nullable=True),
    sa.Column('url', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bookmarks_command'), 'bookmarks', ['command'], unique=True)
    op.create_index(op.f('ix_bookmarks_id'), 'bookmarks', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_bookmarks_id'), table_name='bookmarks')
    op.drop_index(op.f('ix_bookmarks_command'), table_name='bookmarks')
    op.drop_table('bookmarks')
    # ### end Alembic commands ###
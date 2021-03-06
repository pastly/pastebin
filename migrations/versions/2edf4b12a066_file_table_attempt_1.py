"""file table attempt 1

Revision ID: 2edf4b12a066
Revises: f7d5042fda83
Create Date: 2020-12-06 10:18:37.960578

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2edf4b12a066'
down_revision = 'f7d5042fda83'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('file',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('hash', sa.String(length=64), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('hash')
    )
    op.create_table('user_file',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('file_id', sa.Integer(), nullable=False),
    sa.Column('fname', sa.String(length=128), nullable=False),
    sa.Column('ts', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['file_id'], ['file.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'file_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_file')
    op.drop_table('file')
    # ### end Alembic commands ###

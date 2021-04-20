"""empty message

Revision ID: 84b1859f1695
Revises: d2f0a8734534
Create Date: 2020-08-09 16:00:44.994859

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '84b1859f1695'
down_revision = 'd2f0a8734534'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('paymentStates',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=True),
    sa.Column('state', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('paymentStates')
    # ### end Alembic commands ###
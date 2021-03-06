"""empty message

Revision ID: dcbf14c5959e
Revises: 
Create Date: 2020-08-09 14:47:21.601593

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dcbf14c5959e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=64), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('password_ver', sa.String(length=10), nullable=True),
    sa.Column('totalDebt', sa.BigInteger(), server_default='0', nullable=True),
    sa.Column('notConfirmedTotalDebt', sa.BigInteger(), server_default='0', nullable=True),
    sa.Column('confirmedAccount', sa.Boolean(), server_default='0', nullable=True),
    sa.Column('giveAmount', sa.Integer(), server_default='0', nullable=True),
    sa.Column('retAmount', sa.Integer(), server_default='0', nullable=True),
    sa.Column('notConfirmedAmount', sa.Integer(), server_default='0', nullable=True),
    sa.Column('debtsLeft', sa.Integer(), server_default='1000000000', nullable=True),
    sa.Column('isTelegram', sa.Boolean(), server_default='0', nullable=True),
    sa.Column('telegramNick', sa.String(length=128), nullable=True),
    sa.Column('telegramChatId', sa.BigInteger(), server_default='0', nullable=True),
    sa.Column('vaultsAmount', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('vaults',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('total', sa.BigInteger(), nullable=True),
    sa.Column('NotConfirmedTotal', sa.BigInteger(), nullable=True),
    sa.Column('usersAmount', sa.Integer(), nullable=True),
    sa.Column('vault_since', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('debts',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('about', sa.String(length=100), nullable=True),
    sa.Column('total', sa.BigInteger(), server_default='0', nullable=True),
    sa.Column('confirmed', sa.Boolean(), server_default='0', nullable=True),
    sa.Column('refused', sa.Boolean(), server_default='0', nullable=True),
    sa.Column('paid', sa.Boolean(), server_default='0', nullable=True),
    sa.Column('give_id', sa.BigInteger(), nullable=True),
    sa.Column('ret_id', sa.BigInteger(), nullable=True),
    sa.Column('debt_since', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['give_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['ret_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('vaultPayments',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=True),
    sa.Column('vault_id', sa.BigInteger(), nullable=True),
    sa.Column('amount', sa.BigInteger(), nullable=True),
    sa.Column('about', sa.String(length=100), nullable=True),
    sa.Column('acceptedBy', sa.BigInteger(), nullable=True),
    sa.Column('accepted', sa.Boolean(), nullable=True),
    sa.Column('refused', sa.Boolean(), nullable=True),
    sa.Column('payment_since', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['vault_id'], ['vaults.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('vaultSubscriptions',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=True),
    sa.Column('vault_id', sa.BigInteger(), nullable=True),
    sa.Column('state', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['vault_id'], ['vaults.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('paymentStates',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=True),
    sa.Column('payment_id', sa.BigInteger(), nullable=True),
    sa.Column('state', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['payment_id'], ['vaultPayments.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('paymentStates')
    op.drop_table('vaultSubscriptions')
    op.drop_table('vaultPayments')
    op.drop_table('debts')
    op.drop_table('vaults')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###

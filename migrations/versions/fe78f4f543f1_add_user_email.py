"""add user_service_ex-email

Revision ID: fe78f4f543f1
Revises: 8815b51a334d
Create Date: 2024-06-07 01:34:25.235544

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fe78f4f543f1'
down_revision = '8815b51a334d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_service_ex', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email', sa.String(length=50), nullable=False))
        batch_op.drop_constraint('user_username_key', type_='unique')
        batch_op.create_unique_constraint(None, ['email'])
        batch_op.drop_column('username')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_service_ex', schema=None) as batch_op:
        batch_op.add_column(sa.Column('username', sa.VARCHAR(length=50), autoincrement=False, nullable=False))
        batch_op.drop_constraint(None, type_='unique')
        batch_op.create_unique_constraint('user_username_key', ['username'])
        batch_op.drop_column('email')

    # ### end Alembic commands ###

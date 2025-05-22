"""from datetime to int

Revision ID: 02f7da3a1df0
Revises: f0848f59100f
Create Date: 2025-05-22 16:39:23.962397

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '02f7da3a1df0'
down_revision = 'f0848f59100f'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('archived_page') as batch_op:
        batch_op.add_column(sa.Column('timestamp_int', sa.BigInteger(), nullable=True))

    op.execute("""
        UPDATE archived_page
        SET timestamp_int = EXTRACT(EPOCH FROM timestamp)::bigint
    """)

    with op.batch_alter_table('archived_page') as batch_op:
        batch_op.alter_column('timestamp_int', nullable=False)

    with op.batch_alter_table('archived_page') as batch_op:
        batch_op.drop_column('timestamp')

    with op.batch_alter_table('archived_page') as batch_op:
        batch_op.alter_column('timestamp_int', new_column_name='timestamp')


    # ### end Alembic commands ###


def downgrade():
    # 1. Создаём временную колонку для datetime
    with op.batch_alter_table('archived_page') as batch_op:
        batch_op.add_column(sa.Column('timestamp_dt', postgresql.TIMESTAMP(timezone=True), nullable=True))

    # 2. Заполняем эту колонку, конвертируя число в timestamptz
    op.execute("""
        UPDATE archived_page
        SET timestamp_dt = TO_TIMESTAMP(timestamp)
    """)

    # 3. Делаем колонку NOT NULL, если нужно
    with op.batch_alter_table('archived_page') as batch_op:
        batch_op.alter_column('timestamp_dt', nullable=False)

    # 4. Удаляем старую числовую колонку
    with op.batch_alter_table('archived_page') as batch_op:
        batch_op.drop_column('timestamp')

    # 5. Переименовываем новую колонку обратно в timestamp
    with op.batch_alter_table('archived_page') as batch_op:
        batch_op.alter_column('timestamp_dt', new_column_name='timestamp')


    # ### end Alembic commands ###

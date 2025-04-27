"""protected_flag not null

Revision ID: f0848f59100f
Revises: 4b8662853bff
Create Date: 2025-04-26 14:57:01.957444

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f0848f59100f'
down_revision = '4b8662853bff'
branch_labels = None
depends_on = None


def upgrade():
    # Обновление существующих записей, чтобы установить значение False для поля protected
    with op.batch_alter_table('archived_page', schema=None) as batch_op:
        # Сначала обновляем существующие записи
        op.execute("UPDATE archived_page SET protected = False WHERE protected IS NULL")

        # Затем изменяем столбец на not null
        batch_op.alter_column('protected', existing_type=sa.BOOLEAN(), nullable=False)


def downgrade():
    # В случае отката миграции, столбец protected снова может быть nullable
    with op.batch_alter_table('archived_page', schema=None) as batch_op:
        batch_op.alter_column('protected', existing_type=sa.BOOLEAN(), nullable=True)
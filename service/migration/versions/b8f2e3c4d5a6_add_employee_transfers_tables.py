"""add employee transfers tables

Revision ID: b8f2e3c4d5a6
Revises: 19708d2daa51
Create Date: 2025-12-24 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b8f2e3c4d5a6'
down_revision: Union[str, None] = '19708d2daa51'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Создание справочника типов переводов
    op.create_table(
        'dim_transfer_types',
        sa.Column('transfer_type_id', sa.Integer(), primary_key=True),
        sa.Column('transfer_type_name', sa.String(), nullable=False),
    )

    # 2. Заполнение справочника типов переводов
    op.execute("""
        INSERT INTO dim_transfer_types (transfer_type_id, transfer_type_name) VALUES
        (1, 'Перевод между департаментами'),
        (2, 'Изменение должности'),
        (3, 'Изменение Бизнес Юнита'),
        (4, 'Изменение Города'),
        (5, 'Перевод в другую организацию'),
        (6, 'Комплексный перевод')
    """)

    # 3. Создание таблицы истории переводов сотрудников
    op.create_table(
        'employee_transfers',
        sa.Column('transfer_id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('staff_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transfer_date', sa.DateTime(), nullable=True),
        sa.Column('transfer_type_id', sa.Integer(), sa.ForeignKey('dim_transfer_types.transfer_type_id'), nullable=True),

        # Старые значения
        sa.Column('old_department', sa.String(), nullable=True),
        sa.Column('old_position', sa.String(), nullable=True),
        sa.Column('old_city', sa.String(), nullable=True),
        sa.Column('old_unit', sa.String(), nullable=True),
        sa.Column('old_organization', sa.String(), nullable=True),

        # Новые значения
        sa.Column('new_department', sa.String(), nullable=True),
        sa.Column('new_position', sa.String(), nullable=True),
        sa.Column('new_city', sa.String(), nullable=True),
        sa.Column('new_unit', sa.String(), nullable=True),
        sa.Column('new_organization', sa.String(), nullable=True),

        # Метаданные
        sa.Column('update_author', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('comment', sa.String(), nullable=True),

        # Даты
        sa.Column('update_date', sa.DateTime(), default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    # 4. Создание индекса для быстрого поиска по staff_id
    op.create_index('ix_employee_transfers_staff_id', 'employee_transfers', ['staff_id'])


def downgrade() -> None:
    # Удаление индекса
    op.drop_index('ix_employee_transfers_staff_id', table_name='employee_transfers')

    # Удаление таблицы истории переводов
    op.drop_table('employee_transfers')

    # Удаление справочника типов переводов
    op.drop_table('dim_transfer_types')

"""rename_revenu
e_columns

Revision ID: d2391a5ca8eb
Revises: 4c8d9e2b7f1a
Create Date: 2025-11-26 18:48:42.820620

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd2391a5ca8eb'
down_revision: Union[str, None] = '4c8d9e2b7f1a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Переименовываем колонки из camelCase в snake_case
    op.alter_column('revenue_headers', 'countreturns', new_column_name='count_returns')
    op.alter_column('revenue_headers', 'amountWithVATreturns', new_column_name='amount_with_vat_returns')
    op.alter_column('revenue_headers', 'amountWithoutVATreturns', new_column_name='amount_without_vat_returns')
    
    # Изменяем precision для amount полей с numeric(10, 2) на numeric(15, 2)
    op.alter_column('revenue_headers', 'amount_document', 
                   type_=sa.NUMERIC(15, 2), existing_type=sa.NUMERIC(10, 2))
    op.alter_column('revenue_headers', 'amount_card', 
                   type_=sa.NUMERIC(15, 2), existing_type=sa.NUMERIC(10, 2))
    op.alter_column('revenue_headers', 'amount_certificate', 
                   type_=sa.NUMERIC(15, 2), existing_type=sa.NUMERIC(10, 2))
    
    # Добавляем новую колонку delete_status (ее нет в продакшн)
    op.add_column('revenue_headers', sa.Column('delete_status', sa.Boolean(), nullable=True, default=False))


def downgrade() -> None:
    """Downgrade schema."""
    # Убираем новую колонку
    op.drop_column('revenue_headers', 'delete_status')
    
    # Возвращаем precision обратно
    op.alter_column('revenue_headers', 'amount_document', 
                   type_=sa.NUMERIC(10, 2), existing_type=sa.NUMERIC(15, 2))
    op.alter_column('revenue_headers', 'amount_card', 
                   type_=sa.NUMERIC(10, 2), existing_type=sa.NUMERIC(15, 2))
    op.alter_column('revenue_headers', 'amount_certificate', 
                   type_=sa.NUMERIC(10, 2), existing_type=sa.NUMERIC(15, 2))
    
    # Возвращаем старые названия колонок
    op.alter_column('revenue_headers', 'amount_without_vat_returns', new_column_name='amountWithoutVATreturns')
    op.alter_column('revenue_headers', 'amount_with_vat_returns', new_column_name='amountWithVATreturns')
    op.alter_column('revenue_headers', 'count_returns', new_column_name='countreturns')
 
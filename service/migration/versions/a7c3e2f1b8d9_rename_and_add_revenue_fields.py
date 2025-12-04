"""rename and add revenue fields for day-to-day returns

Revision ID: a7c3e2f1b8d9
Revises: 95f8a2b1c4d7
Create Date: 2025-11-07 11:25:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a7c3e2f1b8d9'
down_revision: Union[str, None] = '95f8a2b1c4d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### Переименование существующих полей ###
    op.alter_column('revenue_headers', 'countreturns', new_column_name='count_returns')
    op.alter_column('revenue_headers', 'amountWithVATreturns', new_column_name='amount_with_vat_returns')
    
    # Изменяем тип данных для amount_with_vat_returns с NUMERIC(15,2) на NUMERIC(10,2)
    op.alter_column('revenue_headers', 'amount_with_vat_returns', 
                    type_=sa.NUMERIC(precision=10, scale=2))
    
    # ### Удаляем старое поле amountWithoutVATreturns (оно не нужно) ###
    op.drop_column('revenue_headers', 'amountWithoutVATreturns')
    
    # ### Добавляем новые поля ###
    op.add_column('revenue_headers', sa.Column('delete_status', sa.Boolean(), nullable=True, default=False))
    op.add_column('revenue_headers', sa.Column('amount_without_vat', sa.NUMERIC(precision=10, scale=2), nullable=True, default=0.00))


def downgrade() -> None:
    # ### Откат новых полей ###
    op.drop_column('revenue_headers', 'amount_without_vat')
    op.drop_column('revenue_headers', 'delete_status')
    
    # ### Возврат старого поля ###
    op.add_column('revenue_headers', sa.Column('amountWithoutVATreturns', sa.NUMERIC(precision=15, scale=2), nullable=True, default=0.00))
    
    # ### Возврат старых названий ###
    op.alter_column('revenue_headers', 'amount_with_vat_returns', 
                    type_=sa.NUMERIC(precision=15, scale=2))
    op.alter_column('revenue_headers', 'amount_with_vat_returns', new_column_name='amountWithVATreturns')
    op.alter_column('revenue_headers', 'count_returns', new_column_name='countreturns')

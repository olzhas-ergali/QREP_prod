"""add_amount_fields_to_revenue_headers

Revision ID: 4c8d9e2b7f1a
Revises: 3c394cc326bb
Create Date: 2025-11-06 18:26:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '4c8d9e2b7f1a'
down_revision: Union[str, None] = '822c2bf95d30'  # Последняя миграция
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Добавляем только новые поля по ТЗ (поля для возвратов уже существуют в БД)
    op.add_column('revenue_headers', sa.Column('amount_document', sa.NUMERIC(10, 2), nullable=True, server_default='0.00'))
    op.add_column('revenue_headers', sa.Column('amount_card', sa.NUMERIC(10, 2), nullable=True, server_default='0.00'))
    op.add_column('revenue_headers', sa.Column('amount_certificate', sa.NUMERIC(10, 2), nullable=True, server_default='0.00'))

def downgrade() -> None:
    # Удаляем только новые поля по ТЗ
    op.drop_column('revenue_headers', 'amount_certificate')
    op.drop_column('revenue_headers', 'amount_card')
    op.drop_column('revenue_headers', 'amount_document')

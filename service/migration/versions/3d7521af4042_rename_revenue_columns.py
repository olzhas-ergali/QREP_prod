"""rename_revenue_columns

Revision ID: 3d7521af4042
Revises: a7c3e2f1b8d9
Create Date: 2025-11-19 19:59:33.636264

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d7521af4042'
down_revision: Union[str, None] = 'a7c3e2f1b8d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Переименовываем колонку amount_without_vat в amount_without_vat_returns
    op.alter_column('revenue_headers', 'amount_without_vat', new_column_name='amount_without_vat_returns')


def downgrade() -> None:
    """Downgrade schema."""
    # Возвращаем старое имя колонки
    op.alter_column('revenue_headers', 'amount_without_vat_returns', new_column_name='amount_without_vat')

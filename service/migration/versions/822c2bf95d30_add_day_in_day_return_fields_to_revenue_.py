"""Add day-in-day return fields to revenue_headers

Revision ID: 822c2bf95d30
Revises: 82f7c8366054
Create Date: 2025-10-21 14:49:35.943063

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '822c2bf95d30'
down_revision: Union[str, None] = '82f7c8366054'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('revenue_headers', sa.Column('countreturns', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('revenue_headers', sa.Column('amountWithVATreturns', sa.NUMERIC(10, 2), nullable=False, server_default='0.00'))
    op.add_column('revenue_headers', sa.Column('amountWithoutVATreturns', sa.NUMERIC(10, 2), nullable=False, server_default='0.00'))
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('revenue_headers', 'amountWithoutVATreturns')
    op.drop_column('revenue_headers', 'amountWithVATreturns')
    op.drop_column('revenue_headers', 'countreturns')
    pass

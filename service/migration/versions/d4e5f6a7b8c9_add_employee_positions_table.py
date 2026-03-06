"""add employee_positions table

Revision ID: d4e5f6a7b8c9
Revises: c9f3e4d5a7b8
Create Date: 2026-02-24 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'c9f3e4d5a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'employee_positions',
        sa.Column('position_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('position_name', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('position_id')
    )


def downgrade() -> None:
    op.drop_table('employee_positions')

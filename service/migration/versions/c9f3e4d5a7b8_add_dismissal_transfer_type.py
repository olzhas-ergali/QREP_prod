"""add dismissal transfer type

Revision ID: c9f3e4d5a7b8
Revises: b8f2e3c4d5a6
Create Date: 2026-01-09 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c9f3e4d5a7b8'
down_revision: Union[str, None] = 'b8f2e3c4d5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем тип перевода "Увольнение" (id=7)
    op.execute("""
        INSERT INTO dim_transfer_types (transfer_type_id, transfer_type_name)
        VALUES (7, 'Увольнение')
        ON CONFLICT (transfer_type_id) DO NOTHING
    """)


def downgrade() -> None:
    # Удаляем тип перевода "Увольнение"
    op.execute("""
        DELETE FROM dim_transfer_types WHERE transfer_type_id = 7
    """)

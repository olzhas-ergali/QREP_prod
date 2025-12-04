"""new old rows added

Revision ID: 19708d2daa51
Revises: 3d7521af4042
Create Date: 2025-11-21 19:52:20.892429

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '19708d2daa51'
down_revision: Union[str, None] = '3d7521af4042'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('users_temp', sa.Column('fullname', sa.String(), nullable=True))
    op.add_column('users_temp', sa.Column('iin', sa.String(), nullable=True))
    op.add_column('users_temp', sa.Column('date_receipt', sa.DateTime(), nullable=True))
    op.add_column('users_temp', sa.Column('position_name', sa.String(), nullable=True))
    op.add_column('users_temp', sa.Column('position_id', sa.String(), nullable=True))
    op.add_column('users_temp', sa.Column('organization_name', sa.String(), nullable=True))
    op.add_column('users_temp', sa.Column('organization_id', sa.String(), nullable=True))
    op.add_column('users_temp', sa.Column('organization_bin', sa.String(), nullable=True))
    op.add_column('users_temp', sa.Column('organization_city', sa.String(), nullable=True))
    op.add_column('users_temp', sa.Column('gender', sa.String(), nullable=True))
    op.add_column('users_temp', sa.Column('birth_date', sa.DateTime(), nullable=True))
    op.add_column('users_temp', sa.Column('department', sa.String(), nullable=True))
    op.add_column('users_temp', sa.Column('education', sa.String(), nullable=True))
    op.add_column('users_temp', sa.Column('business_unit', sa.String(), nullable=True))
    op.add_column('users_temp', sa.Column('work_city', sa.String(), nullable=True))

def downgrade() -> None:
    op.drop_column('users_temp', 'work_city')
    op.drop_column('users_temp', 'business_unit')
    op.drop_column('users_temp', 'education')
    op.drop_column('users_temp', 'department')
    op.drop_column('users_temp', 'birth_date')
    op.drop_column('users_temp', 'gender')
    op.drop_column('users_temp', 'organization_city')
    op.drop_column('users_temp', 'organization_bin')
    op.drop_column('users_temp', 'organization_id')
    op.drop_column('users_temp', 'organization_name')
    op.drop_column('users_temp', 'position_id')
    op.drop_column('users_temp', 'position_name')
    op.drop_column('users_temp', 'date_receipt')
    op.drop_column('users_temp', 'iin')
    op.drop_column('users_temp', 'fullname')
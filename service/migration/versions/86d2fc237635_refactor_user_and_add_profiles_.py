"""refactor_user_and_add_profiles_organizations

Revision ID: <ваш_новый_id>
Revises: <id_предыдущей_миграции>
Create Date: <дата>

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '86d2fc237635'
down_revision: Union[str, None] = '82f7c8366054'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table('organizations',
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('organization_name', sa.String(), nullable=True),
        sa.Column('organization_city', sa.String(), nullable=True),
        sa.Column('organization_bin', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('organization_id'),
        sa.UniqueConstraint('organization_bin')
    )
    op.create_table('user_profiles',
        sa.Column('staff_id', sa.UUID(), nullable=False),
        sa.Column('fullname', sa.String(), nullable=True),
        sa.Column('iin', sa.String(), nullable=True),
        sa.Column('gender', sa.String(), nullable=True),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('work_city', sa.String(), nullable=True),
        sa.Column('position_id', sa.String(), nullable=True),
        sa.Column('position_name', sa.String(), nullable=True),
        sa.Column('department', sa.String(), nullable=True),
        sa.Column('business_unit', sa.String(), nullable=True),
        sa.Column('organization_id', sa.UUID(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('date_receipt', sa.DateTime(), nullable=True),
        sa.Column('date_dismissal', sa.DateTime(), nullable=True),
        sa.Column('education', sa.String(), nullable=True),
        sa.Column('local', sa.String(), nullable=True),
        sa.Column('is_admin', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.organization_id']),
        sa.PrimaryKeyConstraint('staff_id'),
        sa.UniqueConstraint('iin')
    )
    
    # Рефакторинг 'users'
    op.add_column('users', sa.Column('staff_id', sa.UUID(), nullable=True))
    op.add_column('users', sa.Column('login_tg', sa.String(), nullable=True))
    op.add_column('users', sa.Column('update_date', sa.DateTime(), nullable=True))
    op.create_foreign_key('fk_users_user_profiles', 'users', 'user_profiles', ['staff_id'], ['staff_id'])
    op.execute('UPDATE users SET login_tg = fullname')
    
    # Удаляем старые, ненужные столбцы
    columns_to_drop_users = ['iin', 'name', 'fullname', 'date_receipt', 'date_dismissal', 'is_active', 'is_admin', 'position_name', 'position_id', 'organization_name', 'organization_bin', 'organization_id']
    for col in columns_to_drop_users:
        op.drop_column('users', col)

    # Рефакторинг 'users_temp'
    op.rename_table('users_temp', 'users_temp_old')
    op.create_table('users_temp',
        sa.Column('staff_id', sa.UUID(), nullable=False),
        sa.Column('phone_number', sa.String(), nullable=True),
        sa.Column('author', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('update_date', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('staff_id')
    )

def downgrade() -> None:
    # Откат рефакторинга 'users_temp'
    op.drop_table('users_temp')
    op.rename_table('users_temp_old', 'users_temp')

    # Откат рефакторинга 'users'
    columns_to_add_users = [
        sa.Column('iin', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('fullname', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('date_receipt', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
        sa.Column('date_dismissal', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
        sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column('is_admin', sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column('position_name', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('position_id', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('organization_name', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('organization_bin', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('organization_id', sa.VARCHAR(), autoincrement=False, nullable=True)
    ]
    op.execute('UPDATE users SET fullname = login_tg')
    for col in columns_to_add_users:
        op.add_column('users', col)

    op.drop_constraint('fk_users_user_profiles', 'users', type_='foreignkey')
    op.drop_column('users', 'update_date')
    op.drop_column('users', 'login_tg')
    op.drop_column('users', 'staff_id')
    
    # Удаление новых таблиц
    op.drop_table('user_profiles')
    op.drop_table('organizations')
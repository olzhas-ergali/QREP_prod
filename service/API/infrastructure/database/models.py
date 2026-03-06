import datetime
import typing
import uuid

from sqlalchemy import (BigInteger, Column, String, select, Date,
                        DateTime, func, Integer, ForeignKey, Boolean,
                        ARRAY, JSON, not_, desc, VARCHAR, Text, CHAR, and_, UUID, DECIMAL, NUMERIC)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.orm import relationship, mapped_column


class Base(DeclarativeBase):
    pass


# 1. НОВАЯ ТАБЛИЦА: organizations
class Organization(Base):
    __tablename__ = "organizations"
    organization_id = mapped_column(UUID(as_uuid=True), primary_key=True)
    organization_name = mapped_column(String)
    organization_city = mapped_column(String, nullable=True)
    organization_bin = mapped_column(String, unique=True)


# Справочник должностей (employee_positions)
class EmployeePosition(Base):
    __tablename__ = "employee_positions"
    position_id = mapped_column(UUID(as_uuid=True), primary_key=True)
    position_name = mapped_column(String, nullable=True)

# 2. НОВАЯ ТАБЛИЦА: user_profiles
class UserProfile(Base):
    __tablename__ = "user_profiles"
    staff_id = mapped_column(UUID(as_uuid=True), primary_key=True)
    fullname = mapped_column(String)
    iin = mapped_column(String, unique=True)
    gender = mapped_column(String, nullable=True)
    birth_date = mapped_column(Date, nullable=True)
    work_city = mapped_column(String, nullable=True)
    position_id = mapped_column(String, nullable=True) # Оставляем String, как в ТЗ
    position_name = mapped_column(String, nullable=True)
    department = mapped_column(String, nullable=True)
    business_unit = mapped_column(String, nullable=True)
    organization_id = mapped_column(UUID(as_uuid=True), ForeignKey('organizations.organization_id'))
    is_active = mapped_column(Boolean, default=True)
    date_receipt = mapped_column(DateTime, nullable=True)
    date_dismissal = mapped_column(DateTime, nullable=True)
    education = mapped_column(String, nullable=True)
    local = mapped_column(String, default="rus")
    is_admin = mapped_column(Boolean, default=False)

    organization = relationship("Organization")


# 3. ОБНОВЛЕННАЯ ТАБЛИЦА: users
class User(Base):
    __tablename__ = "users"
    id = mapped_column(BigInteger, primary_key=True, autoincrement=False) # ID из Telegram
    staff_id = mapped_column(UUID(as_uuid=True), ForeignKey('user_profiles.staff_id'), unique=True, nullable=False)
    phone_number = mapped_column(String, unique=True, nullable=True)
    login_tg = mapped_column(String) # Раньше это было fullname
    author = mapped_column(String, nullable=True)
    created_at = mapped_column(DateTime, server_default=func.now())
    update_date = mapped_column(DateTime, onupdate=func.now(), nullable=True)
    
    profile = relationship("UserProfile", lazy="joined") # lazy="joined" для авто-подгрузки профиля

    @classmethod
    async def get_by_phone(cls, session: AsyncSession, phone: str) -> 'User':
        stmt = select(User).where(phone == User.phone_number)
        return await session.scalar(stmt)
        
    @classmethod
    async def get_by_staff_id(cls, session: AsyncSession, staff_id_val: uuid.UUID) -> 'User':
        stmt = select(User).where(staff_id_val == User.staff_id)
        return await session.scalar(stmt)

    # Старые методы, которые больше не нужны в этой модели
    # get_by_id, get_by_iin, get_by_position_id, get_mention - теперь не актуальны здесь


# 4. ОБНОВЛЕННАЯ ТАБЛИЦА: users_temp
class UserTemp(Base):
    __tablename__ = "users_temp"
    staff_id = mapped_column(UUID(as_uuid=True), primary_key=True)
    phone_number = mapped_column(String, nullable=True)
    author = mapped_column(String, nullable=True)
    created_at = mapped_column(DateTime, server_default=func.now())
    update_date = mapped_column(DateTime, onupdate=func.now(), nullable=True)

    # --- НОВЫЕ ПОЛЯ (из JSON) ---
    fullname = mapped_column(String, nullable=True)
    iin = mapped_column(String, nullable=True)
    date_receipt = mapped_column(DateTime, nullable=True) # Дата приема
    
    # Должность
    position_name = mapped_column(String, nullable=True)
    position_id = mapped_column(String, nullable=True)
    
    # Организация
    organization_name = mapped_column(String, nullable=True)
    organization_id = mapped_column(String, nullable=True) 
    organization_bin = mapped_column(String, nullable=True)
    organization_city = mapped_column(String, nullable=True)
    
    # Личные данные и локация
    gender = mapped_column(String, nullable=True)
    birth_date = mapped_column(DateTime, nullable=True)
    department = mapped_column(String, nullable=True)
    education = mapped_column(String, nullable=True)
    business_unit = mapped_column(String, nullable=True)
    work_city = mapped_column(String, nullable=True)

    @classmethod
    async def get_user_by_iin(cls, session: AsyncSession, iin: str) -> 'UserTemp':
        stmt = select(UserTemp).join(UserProfile, UserTemp.staff_id == UserProfile.staff_id).where(
            (iin == UserProfile.iin) & (UserProfile.is_active == True)
        )
        return await session.scalar(stmt)

class RegTemp(Base):
    __tablename__ = "reg_temp"
    telegram_id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )
    state = Column(
        String
    )
    state_time = Column(
        DateTime, server_default=func.now()
    )
    state_data = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())


class PositionDiscounts(Base):
    __tablename__ = "position_discounts"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    position_id: Column[str] = Column(
        String
    )
    position_name: Column[str] = Column(
        String
    )
    discount_percentage = Column(DECIMAL)
    created_at = Column(DateTime, server_default=func.now())
    update_data = Column(DateTime, default=None)
    is_active = Column(Boolean, default=True)
    description = Column(String, default=None)
    start_date = Column(DateTime, default=None)
    end_date = Column(DateTime, default=None)
    monthly_limit = Column(BigInteger)


class Purchase(Base):
    __tablename__ = "purchases"
    id = Column(String, primary_key=True)
    created_date = Column(DateTime, server_default=func.now())
    user_id = Column(
        BigInteger,
        ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'),
    )
    products = Column(ARRAY(JSON))
    source = Column(String)
    users = relationship(
        'User',
        foreign_keys=[user_id],
        uselist=True,
        lazy='selectin'
    )


class PurchaseReturn(Base):
    __tablename__ = "purchases_return"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    purchase_id = Column(
        String,
        ForeignKey('purchases.id', ondelete='CASCADE'),
    )
    created_date = Column(DateTime, server_default=func.now())
    user_id = Column(
        BigInteger,
        ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'),
    )
    products = Column(ARRAY(JSON))
    return_id = Column(String, default=None)
    source = Column(String)
    users = relationship(
        'User',
        foreign_keys=[user_id],
        uselist=True,
        lazy='selectin'
    )
    purchases = relationship(
        'Purchase',
        foreign_keys=[purchase_id],
        uselist=True,
        lazy='selectin'
    )


class Client(Base):
    __tablename__ = "clients"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    #whatsapp_id = Column(VARCHAR(36))
    name = Column(String)
    fullname = Column(String)
    phone_number = Column(String, unique=True, default=None)
    gender = Column(CHAR)
    birthday_date = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    update_data = Column(DateTime, default=None)
    is_active = Column(Boolean, default=False)
    source = Column(String)
    email = Column(String)
    activity = Column(String, default="telegram")
    local = Column(String, default="rus")

    @classmethod
    async def get_client_by_phone(
            cls,
            session: AsyncSession,
            phone: str
    ) -> 'Client':
        stmt = select(Client).where(
            phone == Client.phone_number
        )

        return await session.scalar(stmt)

    @classmethod
    async def get_client_by_id(
            cls,
            session: AsyncSession,
            client_id: str
    ) -> 'Client':
        stmt = select(Client).where(
            client_id == Client.id
        )

        return await session.scalar(stmt)


class ClientPurchase(Base):
    __tablename__ = "client_purchases"
    id = Column(String, primary_key=True)
    created_date = Column(DateTime, server_default=func.now())
    user_id = Column(
        BigInteger,
        ForeignKey('clients.id', ondelete='CASCADE', onupdate='CASCADE'),
    )
    products = Column(ARRAY(JSON))
    source = Column(String)
    source_system = Column(String)
    order_number = Column(BigInteger)
    number = Column(String)
    shift_number = Column(BigInteger)
    ticket_print_url = Column(String)
    client = relationship(
        'Client',
        foreign_keys=[user_id],
        uselist=True,
        lazy='selectin'
    )
    site_id = Column(String)
    ms_id = Column(String)

    @classmethod
    async def get_by_client_id(
            cls,
            session: AsyncSession,
            client_id: int
    ) -> typing.Sequence['ClientPurchase']:
        stmt = select(ClientPurchase).where(
            client_id == ClientPurchase.user_id
        )
        response = await session.execute(stmt)
        return response.scalars().all()

    @classmethod
    async def get_by_purchase_id(
            cls,
            session: AsyncSession,
            purchase_id: str
    ) -> 'ClientPurchase':
        stmt = select(ClientPurchase).where(
            purchase_id == ClientPurchase.id
        )

        return await session.scalar(stmt)


class ClientPurchaseReturn(Base):
    __tablename__ = "client_purchases_return"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    purchase_id = Column(
        String,
        ForeignKey('client_purchases.id', ondelete='CASCADE'),
    )
    created_date = Column(DateTime, server_default=func.now())
    user_id = Column(
        BigInteger,
        ForeignKey('clients.id', ondelete='CASCADE', onupdate='CASCADE'),
    )
    products = Column(ARRAY(JSON))
    return_id = Column(String, default=None)
    source = Column(String)
    source_system = Column(String)
    order_number = Column(BigInteger)
    number = Column(String)
    shift_number = Column(BigInteger)
    ticket_print_url = Column(String)
    client = relationship(
        'Client',
        foreign_keys=[user_id],
        uselist=True,
        lazy='selectin'
    )
    purchases = relationship(
        'ClientPurchase',
        foreign_keys=[purchase_id],
        uselist=True,
        lazy='selectin'
    )
    site_id = Column(String)
    ms_id = Column(String)

    @classmethod
    async def get_by_purchase_id(
            cls,
            session: AsyncSession,
            purchase_id: str
    ) -> 'ClientPurchaseReturn':
        stmt = select(ClientPurchaseReturn).where(
            purchase_id == ClientPurchaseReturn.purchase_id
        )

        return await session.scalar(stmt)


class ClientReview(Base):
    __tablename__ = "clients_review"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    client_id = Column(
        BigInteger,
        ForeignKey('clients.id', ondelete='CASCADE', onupdate='CASCADE')
    )
    client_review = Column(
        Text
    )
    client_grade = Column(
        Integer
    )
    client_grade_str = Column(
        String
    )
    created_at = Column(DateTime, server_default=func.now())
    clients = relationship(
        'Client',
        foreign_keys=[client_id],
        uselist=True,
        lazy='selectin'
    )

    @classmethod
    async def get_review_by_id(
            cls,
            session: AsyncSession,
            review_id: int
    ) -> 'ClientReview':
        stmt = select(ClientReview).where(
            review_id == ClientReview.id
        )

        return await session.scalar(stmt)


class Revenue(Base):
    __tablename__ = 'revenue_data'
    id = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    document_id = mapped_column(UUID(as_uuid=True))
    # period = mapped_column(DateTime, server_default=func.now())
    product_name = mapped_column(String)
    product_id = mapped_column(UUID(as_uuid=True), default=uuid.uuid4)
    param_name = mapped_column(String)
    param_id = mapped_column(UUID(as_uuid=True), default=uuid.uuid4)
    # Убрал/закоментил 4 поля ниже:
    # warehouse_name = mapped_column(String)
    # warehouse_id = mapped_column(UUID(as_uuid=True), default=uuid.uuid4)
    # organization = mapped_column(String)
    # organization_id = mapped_column(UUID(as_uuid=True), default=uuid.uuid4)
    partner = mapped_column(String)
    phone = mapped_column(String)
    activity_type = mapped_column(String)
    manager = mapped_column(String)
    manager_id = mapped_column(UUID(as_uuid=True), default=uuid.uuid4)
    quantity = mapped_column(Integer)
    revenue_with_vat = mapped_column(Integer)
    revenue_without_vat = mapped_column(Integer)
    currency = mapped_column(String)

    @classmethod
    async def get_revenue(
            cls,
            session: AsyncSession,
            row_id: str,
            document_id: str
    ) -> typing.Optional['Revenue']:
        stmt = select(Revenue).where(and_(Revenue.document_id == document_id, Revenue.row_id == row_id))

        return await session.scalar(stmt)

    @classmethod
    async def get_revenue_by_doc_id(
            cls,
            session: AsyncSession,
            document_id: str
    ) -> typing.Sequence['Revenue']:
        stmt = select(Revenue).where(Revenue.document_id == document_id)
        response = await session.execute(stmt)

        return response.scalars().all()


class RevenueHeaders(Base):
    __tablename__ = 'revenue_headers'
    id = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    document_id = mapped_column(UUID(as_uuid=True))
    document_type = mapped_column(String)
    period = mapped_column(DateTime, nullable=True, default=func.now())
    checks = mapped_column(Integer)
    returns = mapped_column(Integer)
    
    # --- Поля для возвратов "день-в-день" (по новому ТЗ) ---
    delete_status = mapped_column(Boolean, nullable=True, default=False)
    count_returns = mapped_column(Integer, nullable=True, default=0)
    amount_with_vat_returns = mapped_column(NUMERIC(10, 2), nullable=True, default=0.00)
    amount_without_vat_returns = mapped_column(NUMERIC(10, 2), nullable=True, default=0.00)
    
    # --- Новые поля по ТЗ (суммы документа, карт, сертификатов) ---
    amount_document = mapped_column(NUMERIC(15, 2), nullable=True, default=0.00)
    amount_card = mapped_column(NUMERIC(15, 2), nullable=True, default=0.00) 
    amount_certificate = mapped_column(NUMERIC(15, 2), nullable=True, default=0.00)

      # --- Новые поля, смещенные из Revenue

    warehouse_name = mapped_column(String)
    warehouse_id = mapped_column(UUID(as_uuid=True), default=uuid.uuid4)
    organization = mapped_column(String)
    organization_id = mapped_column(UUID(as_uuid=True), default=uuid.uuid4)

    @classmethod
    async def get_revenue_headers_by_doc_id(
            cls,
            session: AsyncSession,
            document_id: str
    ) -> 'RevenueHeaders':
        stmt = select(RevenueHeaders).where(RevenueHeaders.document_id == document_id)
        return await session.scalar(stmt)


class ClientsApp(Base):
    __tablename__ = "clients_app"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=func.now())
    waiting_time = Column(DateTime)
    is_push = Column(Boolean, default=False)
    telegram_id = Column(
        BigInteger,
        default=None
    )
    phone_number = Column(
        String,
        default=None
    )

    @classmethod
    async def get_last_app(
            cls,
            session: AsyncSession,
            telegram_id: int
    ):
        stmt = select(ClientsApp).where((telegram_id == ClientsApp.telegram_id) & (ClientsApp.is_push != True))

        return await session.scalar(stmt)

    @classmethod
    async def get_last_app_by_phone(
            cls,
            session: AsyncSession,
            phone: str
    ):
        stmt = select(ClientsApp).where((phone == ClientsApp.phone_number) & (ClientsApp.is_push != True))

        return await session.scalar(stmt)


class ClientMailing(Base):
    __tablename__ = "clients_mailing"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, server_default=func.now())
    telegram_id = Column(
        BigInteger, default=None
    )
    phone = Column(
        String, default=None
    )

    @classmethod
    async def get_by_phone_number(
            cls,
            phone: str,
            session: AsyncSession
    ) -> typing.Sequence['ClientMailing']:
        stmt = select(ClientMailing).where(ClientMailing.phone == phone)

        return await session.scalar(stmt)



class StaffReview(Base):
    __tablename__ = "staff_review"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    staff_id = Column(
        BigInteger,
        ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE')
    )
    staff_review = Column(
        Text
    )
    staff_grade = Column(
        Integer
    )
    staff_grade_str = Column(
        String
    )
    created_at = Column(DateTime, server_default=func.now())
    
    # Связь с таблицей Users
    user = relationship(
        'User',
        foreign_keys=[staff_id],
        uselist=True,
        lazy='selectin'
    )

    @classmethod
    async def get_review_by_id(
            cls,
            session: AsyncSession,
            review_id: int
    ) -> 'StaffReview':
        stmt = select(StaffReview).where(
            review_id == StaffReview.id
        )
        return await session.scalar(stmt)


# Справочник типов переводов сотрудников
class DimTransferTypes(Base):
    __tablename__ = 'dim_transfer_types'

    transfer_type_id = Column(Integer, primary_key=True)
    transfer_type_name = Column(String, nullable=False)


# Таблица истории переводов сотрудников
class EmployeeTransfers(Base):
    __tablename__ = 'employee_transfers'

    transfer_id = Column(BigInteger, primary_key=True, autoincrement=True)
    staff_id = Column(UUID(as_uuid=True), nullable=False)  # Логическая связь с user_profiles.staff_id
    transfer_date = Column(DateTime, nullable=True)
    transfer_type_id = Column(Integer, ForeignKey('dim_transfer_types.transfer_type_id'), nullable=True)

    # Старые значения (из user_profiles до обновления)
    old_department = Column(String, nullable=True)
    old_position = Column(String, nullable=True)  # position_name
    old_city = Column(String, nullable=True)
    old_unit = Column(String, nullable=True)
    old_organization = Column(String, nullable=True)  # organization_id как строка

    # Новые значения (из JSON)
    new_department = Column(String, nullable=True)
    new_position = Column(String, nullable=True)  # positionName из JSON
    new_city = Column(String, nullable=True)
    new_unit = Column(String, nullable=True)
    new_organization = Column(String, nullable=True)  # organizationId из JSON

    update_author = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    source = Column(String, nullable=True)
    comment = Column(String, nullable=True)  # commentTransfer из JSON

    update_date = Column(DateTime, default=func.now())
    created_at = Column(DateTime, server_default=func.now())

    # Связь со справочником типов
    transfer_type = relationship("DimTransferTypes", lazy="joined")

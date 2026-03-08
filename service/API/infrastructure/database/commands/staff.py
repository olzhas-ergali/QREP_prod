# service/API/infrastructure/database/commands/staff.py

import logging
import typing
import uuid as uuid_module
from datetime import datetime
from typing import Optional
from aiogram import Bot
from fastapi import HTTPException
from sqlalchemy import select, update, extract, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.dialects.postgresql import insert

from service.API.infrastructure.database.models import (User, Purchase, UserTemp, PurchaseReturn, Client,
                                                        PositionDiscounts, UserProfile, Organization,
                                                        EmployeePosition, EmployeeTransfers)

from service.API.infrastructure.database.vacation import StaffVacation, VacationDays
from service.API.infrastructure.models.purchases import ModelUserTemp


def normalize(text: str | None) -> str:
    """Нормализация строки: trim + lowercase"""
    if not text:
        return ""
    return str(text).strip().lower()


def _safe_uuid(value: typing.Any) -> Optional[uuid_module.UUID]:
    """Приведение к UUID; при невалидном значении возвращает None."""
    if value is None:
        return None
    try:
        s = str(value).strip()
        if s.upper().startswith("UUID:"):
            s = s[5:].strip()
        return uuid_module.UUID(s)
    except (ValueError, TypeError, AttributeError):
        return None


def determine_transfer_type(changes: dict) -> int:
    """
    Определение типа перевода по ТЗ:
    1 - Перевод между департаментами (только department)
    2 - Изменение должности (только position)
    3 - Изменение Бизнес Юнита (только unit)
    4 - Изменение Города (только city)
    5 - Перевод в другую организацию (только organization)
    6 - Комплексный перевод (два и более изменений)
    7 - Увольнение (обрабатывается отдельно в add_employees)
    """
    changed_keys = [k for k, v in changes.items() if v]

    if len(changed_keys) == 0:
        return 0  # Нет изменений

    if len(changed_keys) >= 2:
        return 6  # Комплексный перевод

    # Только одно изменение
    key = changed_keys[0]
    type_mapping = {
        'department': 1,
        'position': 2,
        'unit': 3,
        'city': 4,
        'organization': 5
    }
    return type_mapping.get(key, 6)


async def get_user(
        session: AsyncSession,
        phone: str
) -> User:
    stmt = select(User).options(
        selectinload(User.profile)
    ).where(
        User.phone_number == phone
    )
    return await session.scalar(stmt)


async def get_item_count(
        session: AsyncSession,
        user: User | None
):
    if not user or not user.profile:
        return {"itemCount": 0, "availableCount": 0, "discountPercentage": 0.0}

    discount = None
    if user.profile.position_id:
        discount = await get_user_discount(session, user.profile.position_id)

    monthly_limit = 3
    discount_percentage = 30.0
    if discount:
        monthly_limit = discount.monthly_limit
        discount_percentage = discount.discount_percentage

    stmt = select(Purchase).where(
        ((datetime.now().month == extract('month', Purchase.created_date)) &
         (Purchase.user_id == user.id) & (datetime.now().year == extract('year', Purchase.created_date)))
    )
    response = await session.execute(stmt)
    purchases = response.scalars().all()
    count = 0
    products_purchases = []
    purchases_id = []
    for purchase in purchases:
        products = purchase.products
        purchases_id.append(purchase.id)
        for product in products:
            if product.get('discount'):
                products_purchases.append(product.get('price') - product.get('discountPrice'))
                count = count + product['count']
    stmt = select(PurchaseReturn).where(
        ((datetime.now().month == extract('month', PurchaseReturn.created_date)) &
         (datetime.now().year == extract('year', PurchaseReturn.created_date)) &
         (PurchaseReturn.user_id == user.id) &
         (PurchaseReturn.purchase_id.in_(purchases_id)))
    )
    response = await session.execute(stmt)
    purchases_return = response.scalars().all()
    for purchase in purchases_return:
        products = purchase.products
        for product in products:
            if product.get('price') in products_purchases:
                count = count - product['count']
    available_count = monthly_limit - count
    if available_count < 0:
        available_count = 0
    return {
        "itemCount": count,
        "availableCount": available_count,
        "discountPercentage": discount_percentage
    }


async def get_user_discount(
        session: AsyncSession,
        position_id: str
):
    stmt = select(PositionDiscounts).where(position_id == PositionDiscounts.position_id)
    return await session.scalar(stmt)


async def add_employees(
        session: AsyncSession,
        user_data: ModelUserTemp,
        bot: typing.Optional[Bot] = None
):
    """
    Добавление/обновление сотрудника с логикой отслеживания переводов.

    По ТЗ:
    1. Если сотрудник существует - сравнить атрибуты (department, position_id, business_unit, work_city, organization_id)
    2. Если есть изменения - создать запись в employee_transfers, затем обновить user_profiles
    3. Если нет изменений - просто обновить user_profiles
    4. Если сотрудника нет - создать новую запись (новый найм)
    5. Rollback: если данные возвращаются к состоянию до последнего перевода и прошло < 24 часов - удалить последнюю запись
    """
    now = datetime.now()

    clean_date_receipt = user_data.dateOfReceipt if user_data.dateOfReceipt and user_data.dateOfReceipt.year > 1 else None
    clean_date_dismissal = user_data.dateOfDismissal if user_data.dateOfDismissal and user_data.dateOfDismissal.year > 1 else None
    # Дата увольнения не может быть равна дате приёма (приём ≠ увольнение)
    if clean_date_receipt and clean_date_dismissal and clean_date_receipt.date() == clean_date_dismissal.date():
        clean_date_dismissal = None
    if clean_date_receipt and clean_date_dismissal and clean_date_receipt > clean_date_dismissal:
        raise HTTPException(status_code=400, detail="Дата приема не может быть позже даты увольнения.")

    # Приведение id_staff, organization_id, position_id к UUID (при невалидном — логируем и продолжаем)
    staff_uuid = _safe_uuid(user_data.idStaff)
    if staff_uuid is None:
        logging.warning("add_employees: невалидный idStaff (ожидается UUID), idStaff=%s", user_data.idStaff)
        raise HTTPException(status_code=400, detail="Некорректный idStaff (ожидается UUID).")

    org_uuid = _safe_uuid(user_data.organizationId)
    position_uuid = _safe_uuid(user_data.positionId)
    if org_uuid is None and user_data.organizationId:
        logging.warning("add_employees: невалидный organizationId, пропуск записи в organizations: %s", user_data.organizationId)
    if position_uuid is None and user_data.positionId:
        logging.warning("add_employees: невалидный positionId, пропуск записи в employee_positions: %s", user_data.positionId)

    # Флаги для определения результата
    transfer_created = False
    rollback_performed = False

    # 1. Текущий профиль для сравнения (для переводов)
    stmt = select(UserProfile).where(UserProfile.staff_id == staff_uuid)
    existing_profile = await session.scalar(stmt)

    # ЛОГИКА СРАВНЕНИЯ И ПЕРЕВОДОВ (ТОЛЬКО ЕСЛИ СОТРУДНИК УЖЕ СУЩЕСТВУЕТ)
    if existing_profile:
        # Сравниваем атрибуты с нормализацией (trim + lowercase)
        changes = {
            'department': normalize(existing_profile.department) != normalize(user_data.department),
            'position': normalize(existing_profile.position_id) != normalize(user_data.positionId),
            'unit': normalize(existing_profile.business_unit) != normalize(user_data.business_unit),
            'city': normalize(existing_profile.work_city) != normalize(user_data.work_city),
            'organization': normalize(str(existing_profile.organization_id)) != normalize(user_data.organizationId)
        }

        has_changes = any(changes.values())

        # Проверка на увольнение: было активен, стал уволен
        is_dismissal = (
            existing_profile.is_active and
            clean_date_dismissal is not None and
            existing_profile.date_dismissal is None
        )

        if has_changes or is_dismissal:
            # Определение типа перевода (с учётом увольнения)
            if is_dismissal and not has_changes:
                transfer_type_id = 7  # Увольнение
            elif is_dismissal and has_changes:
                transfer_type_id = 6  # Комплексный (увольнение + другие изменения)
            else:
                transfer_type_id = determine_transfer_type(changes)

            # --- ЛОГИКА ROLLBACK (ОТМЕНА ОШИБОЧНОГО ПЕРЕВОДА) ---
            # Проверяем последнюю запись в employee_transfers
            last_transfer_stmt = select(EmployeeTransfers).where(
                EmployeeTransfers.staff_id == staff_uuid
            ).order_by(desc(EmployeeTransfers.created_at)).limit(1)

            last_transfer = await session.scalar(last_transfer_stmt)

            # Сохраняем оригинальные old_* значения из последнего перевода (для использования при создании нового)
            rollback_old_values = None

            # Условие отката:
            # 1. Прошло меньше 24 часов с последнего перевода
            # 2. Новые данные (JSON) совпадают с данными ДО последнего перевода (old_*)
            # Это означает, что сотрудника вернули на прежнее место (отмена ошибочного перевода)
            is_rollback = False
            if last_transfer and last_transfer.created_at:
                time_diff = (now - last_transfer.created_at).total_seconds()
                if time_diff < 86400:  # < 24 часов
                    # Сохраняем old_* значения ДО любых операций
                    rollback_old_values = {
                        'department': last_transfer.old_department,
                        'position': last_transfer.old_position,
                        'city': last_transfer.old_city,
                        'unit': last_transfer.old_unit,
                        'organization': last_transfer.old_organization
                    }
                    # Проверяем, возвращаем ли мы сотрудника в состояние "как было до последнего перевода"
                    if (normalize(user_data.department) == normalize(last_transfer.old_department) and
                        normalize(user_data.positionName) == normalize(last_transfer.old_position) and
                        normalize(user_data.work_city) == normalize(last_transfer.old_city) and
                        normalize(user_data.business_unit) == normalize(last_transfer.old_unit) and
                        normalize(user_data.organizationId) == normalize(last_transfer.old_organization)):
                        is_rollback = True

            if is_rollback:
                # Удаляем последнюю ошибочную запись о переводе
                # Новый перевод НЕ создаем - сотрудник вернулся на прежнее место
                await session.delete(last_transfer)
                rollback_performed = True
            else:
                # Если есть предыдущий перевод < 24ч - удаляем его (ошибочный)
                if rollback_old_values and last_transfer:
                    await session.delete(last_transfer)
                    rollback_performed = True

                # Создаем новую запись о переводе
                # При наличии rollback_old_values используем их для old_* полей
                new_transfer = EmployeeTransfers(
                    staff_id=staff_uuid,
                    transfer_date=user_data.updateDate or now,
                    transfer_type_id=transfer_type_id,

                    # Старые значения (из rollback или из профиля)
                    old_department=rollback_old_values['department'] if rollback_old_values else existing_profile.department,
                    old_position=rollback_old_values['position'] if rollback_old_values else existing_profile.position_name,
                    old_city=rollback_old_values['city'] if rollback_old_values else existing_profile.work_city,
                    old_unit=rollback_old_values['unit'] if rollback_old_values else existing_profile.business_unit,
                    old_organization=rollback_old_values['organization'] if rollback_old_values else (str(existing_profile.organization_id) if existing_profile.organization_id else None),

                    # Новые значения (из JSON)
                    new_department=user_data.department,
                    new_position=user_data.positionName,
                    new_city=user_data.work_city,
                    new_unit=user_data.business_unit,
                    new_organization=user_data.organizationId,

                    update_author=user_data.author,
                    is_active=(clean_date_dismissal is None),
                    source="1C",
                    comment=user_data.commentTransfer
                )
                session.add(new_transfer)
                transfer_created = True

    # --- Порядок по ТЗ: staff_vacation → users_temp → vacation_days → organizations → employee_positions → user_profiles → employee_transfers (уже выше при has_changes) → commit ---

    # 1. StaffVacation (staff_vacation, vacation_days)
    vacation_stmt = insert(StaffVacation).values(
        fullname=user_data.fullname,
        iin=user_data.iin,
        date_receipt=clean_date_receipt,
        guid=str(staff_uuid),
        is_fired=(clean_date_dismissal is not None)
    ).on_conflict_do_update(
        index_elements=['iin'],
        set_={
            'fullname': user_data.fullname,
            'date_receipt': clean_date_receipt,
            'guid': str(staff_uuid),
            'is_fired': (clean_date_dismissal is not None)
        }
    )
    await session.execute(vacation_stmt)

    # 2. UserTemp (users_temp: get or create, обновить поля)
    temp_stmt = insert(UserTemp).values(
        staff_id=staff_uuid,
        phone_number=user_data.phone,
        author=user_data.author,
        update_date=user_data.updateDate,
        fullname=user_data.fullname,
        iin=user_data.iin,
        date_receipt=user_data.dateOfReceipt,
        position_name=user_data.positionName,
        position_id=user_data.positionId,
        organization_name=user_data.organizationName,
        organization_id=str(org_uuid) if org_uuid else user_data.organizationId,
        organization_bin=user_data.organizationBin,
        organization_city=user_data.organizationCity,
        gender=user_data.gender,
        birth_date=user_data.birthDate,
        department=user_data.department,
        education=user_data.education,
        business_unit=user_data.business_unit,
        work_city=user_data.work_city
    ).on_conflict_do_update(
        index_elements=['staff_id'],
        set_={
            'phone_number': user_data.phone,
            'author': user_data.author,
            'update_date': user_data.updateDate,
            'fullname': user_data.fullname,
            'iin': user_data.iin,
            'date_receipt': user_data.dateOfReceipt,
            'position_name': user_data.positionName,
            'position_id': user_data.positionId,
            'organization_name': user_data.organizationName,
            'organization_id': str(org_uuid) if org_uuid else user_data.organizationId,
            'organization_bin': user_data.organizationBin,
            'organization_city': user_data.organizationCity,
            'gender': user_data.gender,
            'birth_date': user_data.birthDate,
            'department': user_data.department,
            'education': user_data.education,
            'business_unit': user_data.business_unit,
            'work_city': user_data.work_city
        }
    )
    await session.execute(temp_stmt)

    # 3. Инициализация VacationDays (если нет)
    staff_vac_obj = await StaffVacation.get_by_iin(iin=user_data.iin, session=session)
    if staff_vac_obj:
        current_year = datetime.now().year
        vac_days_stmt = select(VacationDays).where(
            (VacationDays.staff_vac_id == staff_vac_obj.id) &
            (VacationDays.year == current_year)
        )
        vac_days_exists = await session.scalar(vac_days_stmt)
        if not vac_days_exists:
            new_vac_days = VacationDays(
                staff_vac_id=staff_vac_obj.id,
                year=current_year,
                days=0,
                dbl_days=0.0,
                vacation_start=None,
                vacation_end=None
            )
            session.add(new_vac_days)

    # 4. Organizations (upsert по organization_id)
    if org_uuid is not None:
        org_bin = user_data.organizationBin or str(org_uuid)
        org_stmt = insert(Organization).values(
            organization_id=org_uuid,
            organization_name=user_data.organizationName,
            organization_city=user_data.organizationCity,
            organization_bin=org_bin
        ).on_conflict_do_update(
            index_elements=['organization_id'],
            set_={
                'organization_name': user_data.organizationName,
                'organization_city': user_data.organizationCity,
                'organization_bin': org_bin
            }
        )
        await session.execute(org_stmt)

    # 5. Employee positions (upsert по position_id)
    if position_uuid is not None and (user_data.positionName or user_data.positionId):
        pos_stmt = insert(EmployeePosition).values(
            position_id=position_uuid,
            position_name=user_data.positionName or str(user_data.positionId)
        ).on_conflict_do_update(
            index_elements=['position_id'],
            set_={'position_name': user_data.positionName or str(user_data.positionId)}
        )
        await session.execute(pos_stmt)

    # 6. User profiles (get or create + обновить все поля из запроса)
    profile_stmt = insert(UserProfile).values(
        staff_id=staff_uuid,
        fullname=user_data.fullname,
        iin=user_data.iin,
        gender=user_data.gender,
        birth_date=user_data.birthDate,
        work_city=user_data.work_city,
        position_id=user_data.positionId,
        position_name=user_data.positionName,
        department=user_data.department,
        business_unit=user_data.business_unit,
        organization_id=org_uuid,
        is_active=(clean_date_dismissal is None),
        date_receipt=clean_date_receipt,
        date_dismissal=clean_date_dismissal,
        education=user_data.education,
        is_admin=False
    ).on_conflict_do_update(
        index_elements=['staff_id'],
        set_={
            'fullname': user_data.fullname,
            'gender': user_data.gender,
            'birth_date': user_data.birthDate,
            'work_city': user_data.work_city,
            'position_id': user_data.positionId,
            'position_name': user_data.positionName,
            'department': user_data.department,
            'business_unit': user_data.business_unit,
            'organization_id': org_uuid,
            'is_active': (clean_date_dismissal is None),
            'date_receipt': clean_date_receipt,
            'date_dismissal': clean_date_dismissal,
            'education': user_data.education
        }
    )
    await session.execute(profile_stmt)

    await session.commit()

    # Формирование ответа по ТЗ
    if rollback_performed:
        return {
            "id": user_data.idStaff,
            "message": "Последний перевод был удален, новый перевод успешно переведен",
            "status_code": 201
        }
    elif transfer_created:
        return {
            "id": user_data.idStaff,
            "message": "Сотрудник успешно переведен.",
            "status_code": 201
        }
    else:
        return {
            "id": user_data.idStaff,
            "message": "Сотрудник успешно создан/обновлен."
        }


async def get_user_by_iin(
        session: AsyncSession,
        iin: str
) -> UserProfile:
    stmt = select(UserProfile).where(UserProfile.iin == iin)
    return await session.scalar(stmt)


async def get_staff_by_iin(
        session: AsyncSession,
        iin: str
) -> User:
    stmt = select(User).join(UserProfile, User.staff_id == UserProfile.staff_id).where(UserProfile.iin == iin)
    return await session.scalar(stmt)

# Функции ниже, скорее всего, устарели, но на всякий случай оставляем их пустыми или с минимальной логикой
# чтобы избежать ошибок импорта в других частях программы.

async def get_purchases_count(session: AsyncSession, user_id: int):
    return {"itemCount": 0}

async def add_purchases(session: AsyncSession, **kwargs):
    return {}

async def add_return_purchases(session: AsyncSession, **kwargs):
    return {}

async def add_user_temp(session: AsyncSession, **kwargs):
    return {}

async def get_all_purchases(session: AsyncSession, user_id: int):
    return []

async def get_purchases_by_month(session: AsyncSession, date: Optional[datetime], user_id: int):
    return []

async def is_return_purchases(session: AsyncSession, **kwargs):
    return False

# service/API/infrastructure/database/commands/staff.py

import logging
import typing
from datetime import datetime
from typing import Optional
from aiogram import Bot
from fastapi import HTTPException
from sqlalchemy import select, update, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.dialects.postgresql import insert

from service.API.infrastructure.database.models import (User, Purchase, UserTemp, PurchaseReturn, Client,
                                                        PositionDiscounts, UserProfile, Organization)

from service.API.infrastructure.database.vacation import StaffVacation, VacationDays
from service.API.infrastructure.models.purchases import ModelUserTemp


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
    now = datetime.now()

    clean_date_receipt = user_data.dateOfReceipt if user_data.dateOfReceipt and user_data.dateOfReceipt.year > 1 else None
    clean_date_dismissal = user_data.dateOfDismissal if user_data.dateOfDismissal and user_data.dateOfDismissal.year > 1 else None
    if clean_date_receipt and clean_date_dismissal and clean_date_receipt > clean_date_dismissal:
        raise HTTPException(status_code=400, detail="Дата приема не может быть позже даты увольнения.")

    org_stmt = insert(Organization).values(
        organization_id=user_data.organizationId,
        organization_name=user_data.organizationName,
        organization_city=user_data.organizationCity,
        organization_bin=user_data.organizationBin
    ).on_conflict_do_update(
        index_elements=['organization_id'],
        set_={
            'organization_name': user_data.organizationName,
            'organization_city': user_data.organizationCity,
            'organization_bin': user_data.organizationBin
        }
    )
    await session.execute(org_stmt)

    profile_stmt = insert(UserProfile).values(
        staff_id=user_data.idStaff,
        fullname=user_data.fullname,
        iin=user_data.iin,
        gender=user_data.gender,
        birth_date=user_data.birthDate,
        work_city=user_data.work_city,
        position_id=user_data.positionId,
        position_name=user_data.positionName,
        department=user_data.department,
        business_unit=user_data.business_unit,
        organization_id=user_data.organizationId,
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
            'organization_id': user_data.organizationId,
            'is_active': (clean_date_dismissal is None),
            'date_receipt': clean_date_receipt,
            'date_dismissal': clean_date_dismissal,
            'education': user_data.education
        }
    )
    await session.execute(profile_stmt)

    # 3. StaffVacation (ДОБАВЛЕНО ИСПРАВЛЕНИЕ ДЛЯ ПРОБЛЕМЫ №1)
    vacation_stmt = insert(StaffVacation).values(
        fullname=user_data.fullname,
        iin=user_data.iin,
        date_receipt=clean_date_receipt,
        is_fired=(clean_date_dismissal is not None)
    ).on_conflict_do_update(
        index_elements=['iin'], 
        set_={
            'fullname': user_data.fullname,
            'date_receipt': clean_date_receipt,
            'is_fired': (clean_date_dismissal is not None)
        }
    )
    await session.execute(vacation_stmt)

    temp_stmt = insert(UserTemp).values(
        staff_id=user_data.idStaff,
        phone_number=user_data.phone, 
        author=user_data.author,
        update_date=user_data.updateDate,
        
        # Новые поля
        fullname=user_data.fullname,
        iin=user_data.iin,
        date_receipt=user_data.dateOfReceipt,
        
        position_name=user_data.positionName,
        position_id=user_data.positionId,
        
        organization_name=user_data.organizationName,
        organization_id=user_data.organizationId,
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
            'organization_id': user_data.organizationId,
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
    
    await session.commit()
    
    return {"id": user_data.idStaff, "message": "Сотрудник успешно создан/обновлен."}


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
import typing
from datetime import datetime
from uuid import UUID

from typing import Sequence, Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import ArgumentError
from service.API.infrastructure.database.models import Revenue, RevenueHeaders
from service.API.infrastructure.models.revenue import RevenueDateModel


async def add_revenue_date(
        revenue: RevenueDateModel,
        session: AsyncSession,
        document_id: str = None
):
    msg = "Данные успешно добавлены в базу данных"
    try:
        documents = await Revenue.get_revenue_by_doc_id(session=session, document_id=revenue.documentId)
        rh = await RevenueHeaders().get_revenue_headers_by_doc_id(session=session, document_id=revenue.documentId)
        if rh:
            await session.delete(rh)
            await session.commit()
        if documents:
            for i in documents:
                msg = "Данные успешно обновлены"
                await session.delete(i)
                await session.commit()
        if revenue.deleteStatus:
            msg = "Данные успешно удалены"
        else:
            rh = RevenueHeaders()
            rh.document_id = revenue.documentId
            rh.period = revenue.period
            rh.document_type = revenue.documentType
            rh.checks = revenue.checks
            rh.returns = revenue.returns
            
            # --- Поля для возвратов "день-в-день" (по новому ТЗ) ---
            rh.delete_status = revenue.deleteStatus 
            rh.count_returns = revenue.count_returns 
            rh.amount_with_vat_returns = revenue.amount_with_vat_returns 
            rh.amount_without_vat_returns = revenue.amount_without_vat_returns 
            
            # --- Новые поля по ТЗ (суммы документа, карт, сертификатов) ---
            rh.amount_document = revenue.amountDocument 
            rh.amount_card = revenue.amountCard 
            rh.amount_certificate = revenue.amountCertificate

            # --- Перенос warehouse и organization из Revenue в RevenueHeaders ---
            if revenue.data:
                first_item = revenue.data[0]
                rh.warehouse_name = first_item.get('warehouseName')
                rh.warehouse_id = first_item.get('warehouseId')
                rh.organization = first_item.get('organization')
                rh.organization_id = first_item.get('organizationId')
            else:
                rh.warehouse_name = revenue.warehouseName
                rh.warehouse_id = UUID(str(revenue.warehouseId)) if revenue.warehouseId else None

                rh.organization = revenue.organization
                rh.organization_id = UUID(str(revenue.organizationId)) if revenue.organizationId else None

            
            session.add(rh)
            await session.commit()
            
        if revenue.data:
            for r_item in revenue.data:
                #if not (r := await Revenue.get_revenue(session, r_item.get('row_id'), revenue.documentId)):
                #if not (r := await Revenue.get_revenue(session, r_item.get('row_id'), document_id)):
                # r.row_id = r_item.get('row_id')
                r = Revenue()
                r.document_id = revenue.documentId
                #r.period = revenue.period
                r.manager = r_item.get('manager')
                r.manager_id = r_item.get('managerId')
                r.revenue_with_vat = r_item.get('revenueWithVAT')
                r.revenue_without_vat = r_item.get('revenueWithoutVAT')
                r.phone = r_item.get('phone')
                # -- Закоментил 2 поля ниже ---
                # r.warehouse_name = r_item.get('warehouseName')
                # r.warehouse_id = r_item.get('warehouseId')
                r.product_id = r_item.get('productId')
                r.product_name = r_item.get('productName')
                r.currency = r_item.get('currency')
                r.activity_type = r_item.get('activityType')
                # -- Закоментил 2 поля ниже ---
                # r.organization = r_item.get('organization')
                # r.organization_id = r_item.get('organizationId')
                r.param_id = r_item.get('paramId')
                r.param_name = r_item.get('paramName')
                r.partner = r_item.get('partner')
                r.quantity = r_item.get('quantity')
                session.add(r)
                await session.commit()
    except TypeError:
        raise HTTPException(status_code=422, detail="Неверный формат данных")
    except ArgumentError:
        raise HTTPException(status_code=402, detail="Недостаточно данных")
    return {
        'status_code': '200',
        'id': revenue.documentId,
        "message": msg
    }


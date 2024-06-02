import logging

from aiogram import Bot
import openpyxl
from openpyxl.worksheet.worksheet import Worksheet
from sqlalchemy.ext.asyncio import AsyncSession

from service.tgbot.models.database.users import UserTemp
from service.tgbot.misc.parse import parse_phone


class StaffManager:

    @classmethod
    async def add_staff(
            cls,
            file_name: str,
            session: AsyncSession,
    ):
        wb = openpyxl.load_workbook(file_name)
        ws: Worksheet = wb.active

        for row in ws.iter_rows(min_row=1, min_col=1, max_col=2, values_only=True):
            phone_number = parse_phone(row[0])
            name = str(row[1]).strip()
            if not await session.get(UserTemp, phone_number):
                user_t = UserTemp(
                    phone_number=phone_number,
                    name=name
                )
                session.add(user_t)
                await session.commit()


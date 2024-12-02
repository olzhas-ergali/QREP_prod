from aiogram.types.callback_query import CallbackQuery
from aiogram.dispatcher.storage import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from service.tgbot.models.database.users import Client, ClientMailing
from service.tgbot.handlers.client.faq.main import faq_lvl_handler


async def mailing_handler(
        callback: CallbackQuery,
        session: AsyncSession,
        callback_data: dict,
        state: FSMContext,
        user: Client,
):
    text = '''
Вы вернулись к основному меню. Чем еще можем помочь?

Сіз басты бетке оралдыңыз. Тағы қандай көмек көрсете аламыз?
'''
    if callback_data.get('lvl') == 'yes':
        c = ClientMailing(
            telegram_id=user.id
        )
        session.add(c)
        await session.commit()
        text = '''
Вы подписались на уведомление

Вы вернулись к основному меню. Чем еще можем помочь?

Сіз басты бетке оралдыңыз. Тағы қандай көмек көрсете аламыз?
        '''
    callback_data['lvl'] = 'main'
    await faq_lvl_handler(
        callback=callback,
        callback_data=callback_data,
        state=state,
        text=text
    )

import os
import segno
import datetime
import logging

from aiogram.types.message import Message, ContentType
from aiogram.types.callback_query import CallbackQuery
from aiogram.dispatcher.storage import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from service.tgbot.models.database.users import Client
from service.tgbot.models.database.cods import Cods
from service.tgbot.modules.OneС.Function_1C import get_balance
from service.tgbot.misc.delete import remove
from service.tgbot.keyboards.client.faq import get_faq_btns
from service.tgbot.misc.generate import generate_code
from service.tgbot.models.database.loyalty import ClientBonusPoints


async def main_handler(
        m: Message | CallbackQuery
):
    _ = m.bot.get("i18n")
    btns = await get_faq_btns('main', _)
    if isinstance(m, Message):
        return await m.answer(
            text=_("Чем могу помочь? Выберите одну из опций:"),
            reply_markup=btns
        )
    return await m.message.answer(
        text=_("Чем могу помочь? Выберите одну из опций:"),
        reply_markup=btns
    )


async def start_handler(
        message: Message,
        user: Client,
        session: AsyncSession,
        state: FSMContext
):
    _ = message.bot.get("i18n")
    await state.finish()
    await remove(message, 1)
    await remove(message, 0)
    logging.info(f"Клиент с id: {user.id} авторизовался/зарегался в боте")
    gender = 'Дорогой'
    if user.gender == b'M' or user.gender == 'M':
        gender = 'Дорогой'
    elif user.gender == b'F' or user.gender == 'F':
        gender = 'Дорогая'
    if user.local == 'kaz':
        gender = 'Құрметті'
    text = _("{gender} {name}, вас приветствует команда Qazaq Republic!🤗\n").format(gender=gender, name=user.name)
    await message.answer(
        text=text
        #reply_markup=await main_btns(_)
    )
    await main_handler(message)


async def get_my_qr_handler(
        callback: CallbackQuery,
        user: Client,
        session: AsyncSession,
        state: FSMContext
):
    _ = callback.bot.get('i18n')
    await state.finish()
    text = _("Вы уже сгенерировали QR, дождитесь 15 минут, чтобы сгенерировать QR")
    qrcode = None
    code = await Cods.get_cody_by_phone(user.phone_number, session)
    if not code or (code and code.is_active) or (datetime.datetime.now() - code.created_at).total_seconds()/60 > 15:
        text = _('''
Это ваш персональный QR-код для начисления и списания кэшбэка.
Обязательно покажите его кассиру перед оплатой, чтобы получить кэшбэк или использовать накопленный.
''')
        code = await generate_code(session, phone_number=user.phone_number)
        qrcode = segno.make(code.code, micro=False)
        qrcode.save(user.phone_number + ".png", border=4, scale=7)

    await callback.message.delete()
    if qrcode:
        await callback.message.answer_photo(
            photo=open(user.phone_number + ".png", "rb"),
            caption=text,
        )
        try:
            os.remove(user.phone_number + ".png")
        except:
            pass
    else:
        await callback.message.answer(
            text=text
        )
    btns = await get_faq_btns('main', _)
    await callback.message.answer(
        text=_("Чем могу помочь? Выберите одну из опций:"),
        reply_markup=btns
    )


async def get_my_bonus_handler(
        callback: CallbackQuery,
        session: AsyncSession,
        user: Client,
        state: FSMContext
):
    _ = callback.bot.get('i18n')
    await state.finish()
    await callback.message.delete()
    client_bonuses = await ClientBonusPoints.get_all_by_client_id(session=session, client_id=user.id)
    available_bonus = 0
    future_bonus = 0
    if client_bonuses:
        total_earned = 0
        total_spent = 0
        total_future_spent = 0
        total_future_earned = 0
        for bonus in client_bonuses:
            logging.info(f"accrued_points: {bonus.accrued_points}")
            logging.info(f"write_off_points: {bonus.write_off_points}")
            if bonus.expiration_date.date() < datetime.datetime.now().date():
                if datetime.datetime.now().date() >= bonus.activation_date.date() or bonus.expiration_date.date() is None:
                    total_earned += bonus.accrued_points if bonus.accrued_points else 0
                    total_spent += bonus.write_off_points if bonus.write_off_points else 0
                else:
                    total_future_earned += bonus.accrued_points if bonus.accrued_points else 0
                    total_future_spent += bonus.write_off_points if bonus.write_off_points else 0
        if total_earned > 0:
            available_bonus += total_earned
        if total_spent > 0:
            available_bonus -= total_spent
        if total_future_earned > 0:
            future_bonus += total_future_earned
        if total_future_spent > 0:
            future_bonus -= total_future_spent
    await callback.message.answer(
        _('''
Ваш баланс кэшбэка: {cashback} 
Если сумма равна 0 , это может означать, что:
• вы ещё не совершали покупок, или
• кэшбэк по вашему заказу ещё не начислен — он будет зачислен на бонусный счёт через 14 дней после покупки.

Ожидаемая сумма начисления: {future_bonus}
''').format(cashback=available_bonus if available_bonus > 0 else 0, future_bonus=future_bonus)
    )
    btns = await get_faq_btns('main', _)
    await callback.message.answer(
        text=_("Чем могу помочь? Выберите одну из опций:"),
        reply_markup=btns
    )
#     res, msg = await get_balance(
#         user=user,
#         bot=callback.bot
#     )
#     await callback.message.delete()
#     if res == 0:
#         await callback.message.answer(
#             text=_('''У вас пока нет накопленных бонусов.
# Совершайте покупки и участвуйте в наших акциях,
# чтобы начать зарабатывать баллы!''')
#         )
#     else:
#         await callback.message.answer(
#             text=_("У вас: {res} бонусов {msg}").format(res=res, msg=msg),
#         )

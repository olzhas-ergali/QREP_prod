import os
import segno
import datetime

from aiogram.types import InlineKeyboardMarkup
from aiogram.types.message import Message, ContentType
from aiogram.types.callback_query import CallbackQuery
from aiogram.dispatcher.storage import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from service.tgbot.models.database.users import Client, ClientMailing, ClientsApp
from service.tgbot.keyboards.client.faq import get_faq_btns_new, get_faq_ikb, get_times, get_grade_btns
from service.tgbot.data.faq import faq_texts2
from service.tgbot.misc.states.client import FaqState
from service.tgbot.misc.delete import remove


async def get_faq_handler(
        message: Message,
        state: FSMContext
):
    await message.delete()
    await state.finish()
    btns, items = await get_faq_btns_new(faq_texts2)
    await message.answer(
        text="Выберите раздел",
        reply_markup=btns
    )
    await state.update_data(items=items)
    await FaqState.start.set()


async def faq_chapters_handler(
        callback: CallbackQuery,
        callback_data: dict,
        state: FSMContext
):
    data = await state.get_data()
    chapter = callback_data.get('chapter')

    text = "Выберите раздел"
    if chapter != "back":
        q_text = callback.message.reply_markup.inline_keyboard[int(chapter)][0].text
        #if q_text == "На русском":
        #    q_text = "rus"
        #if q_text == "На казахском":
        #    q_text = "kaz"
        if q_text in ['Проблема по доставке', 'Не прошла оплата', 'Подключить оператора']:
            await FaqState.waiting_operator.set()
        else:
            await FaqState.start.set()

        if data.get('prev_items'):
            prev_items = data.get('prev_items') + ":" + q_text
        else:
            prev_items = q_text
        data['items'] = data['items'].get(q_text)
        await state.update_data(prev_items=prev_items)
    else:
        data['items'] = faq_texts2
        data_items = data.get('prev_items').split(":")
        for i in data_items[:len(data_items) - 1]:
            data['items'] = data['items'].get(i)
        await state.update_data(prev_items=":".join(data_items[:len(data_items) - 1]))
    btn, items = await get_faq_btns_new(curr_items=data.get('items'))
    if isinstance(items, str):
        text = items
    await callback.message.edit_text(
        text=text,
        reply_markup=btn
    )

    await state.update_data(items=items)


async def mailing_handler(
        callback: CallbackQuery,
        session: AsyncSession,
        callback_data: dict,
        state: FSMContext,
        user: Client,
):
    btns, items = await get_faq_btns_new(faq_texts2)
    await state.finish()
    if callback_data.get('answer') == 'yes':
        c = ClientMailing(
            telegram_id=user.id
        )
        session.add(c)
        await session.commit()
        await callback.message.edit_text(
            text='''
Вы подписались на уведомление
 
Вы вернулись к основному меню. Чем еще можем помочь?

Сіз басты бетке оралдыңыз. Тағы қандай көмек көрсете аламыз?
''',
            reply_markup=btns
        )
    else:
        await callback.message.edit_text(
            text='''
Вы вернулись к основному меню. Чем еще можем помочь?

Сіз басты бетке оралдыңыз. Тағы қандай көмек көрсете аламыз?
        ''',
            reply_markup=btns
        )

    await state.update_data(items=items)
    await FaqState.start.set()


async def operator_handler(
        message: Message,
        session: AsyncSession,
        state: FSMContext,
        user: Client,
):
    await message.delete()
    await remove(message, 1)
    await message.answer(
        text='''
Вы выбрали опцию подключить оператора. Хотите, чтобы я подключил оператора сейчас или позже? Пожалуйста, выберите подходящий вариант:

Сіз операторменн байланысу опциясын белгіледіңіз. Біз операторды қандай уақыт аралығында қосуымыз қажет? Төменде көрсетілген уақытты белгілеуіңізді сұраймыз: 
''',
        reply_markup=await get_times()
    )
    await FaqState.waiting_time.set()


async def send_operator_handler(
        callback: CallbackQuery,
        session: AsyncSession,
        state: FSMContext,
        user: Client,
        callback_data: dict
):
    btns, items = await get_faq_btns_new(faq_texts2)
    waiting_time = callback_data.get('time')
    date = datetime.datetime.now() + datetime.timedelta(minutes=int(waiting_time) + 5)
    text = '''
Вы уже подавали заявку, подождите пока оператор ответит на ваш запрос
'''
    if not (c := await ClientsApp.get_last_app(
        session=session,
        telegram_id=user.id
    )):
        text = '''
Спасибо за выбор! Оператор свяжется с вами в указанное время.

Таңдағаныңыз үшін рақмет! Оператор сізбен көрсетілген уақытта хабарласады.
        '''
        c = ClientsApp(
            telegram_id=user.id,
            waiting_time=date
        )
        session.add(c)
        await session.commit()
    await callback.message.edit_text(
        text=text
    )
    await callback.message.answer(
        text='''
Вы вернулись к основному меню. Чем еще можем помочь?

Сіз басты бетке оралдыңыз. Тағы қандай көмек көрсете аламыз?
            ''',
        reply_markup=btns
    )
    await state.update_data(items=items)
    await FaqState.start.set()


async def user_wait_answer_handler(
        callback: CallbackQuery,
        session: AsyncSession,
        state: FSMContext,
        user: Client,
        callback_data: dict
):
    await state.finish()
    if callback_data.get('ans') == 'yes':
        return await user_grade_handler(
            callback=callback,
            session=session,
            state=state,
            user=user
        )
    await operator_handler(
        message=callback.message,
        session=session,
        state=state,
        user=user
    )


async def user_grade_handler(
        callback: CallbackQuery,
        session: AsyncSession,
        state: FSMContext,
        user: Client
):
    await callback.message.edit_text(
        text='Оцените работу оператора от 1 до 5',
        reply_markup=get_grade_btns()
    )


async def user_graded_handler(
        callback: CallbackQuery,
        session: AsyncSession,
        state: FSMContext,
        user: Client,
        callback_data: dict
):
    btns, items = await get_faq_btns_new(faq_texts2)
    await state.finish()
    texts = {
        True: '''
Сіздің қызмет көрсету ұпайыңыз 4-тен төмен екенін байқадық.
Туындаған қолайсыздық жайлы ақпаратпен бөліссеңіз, біз алдағы уақытта қызметімізді жақсарту үшін шаралар қабылдаймыз.
Түсіністік таңытқаныңыз үшін рақмет және Сіздің жауабыңызды асыға күтеміз.
Құрметпен, Qazaq Republic
_________________________________________________
Мы заметили, что Ваша оценка обслуживания ниже 4.
Если вы поделитесь информацией о причиненных неудобствах, мы примем меры для улучшения нашего сервиса в будущем.
Благодарим вас за понимание и с нетерпением ждем вашего ответа.
С уважением, Qazaq Republic
''',
        False: '''
Бізді таңдағаныңыз үшін рақмет! Сізді тағы күтеміз:)
Құрметпен, Qazaq Republic💙

__________________________________


Благодарим Вас за выбор наших услуг! Будем ждать Вас еще:)
С уважением, Qazaq Republic💙'''
    }
    await callback.message.edit_text(
        text=texts.get(callback_data.get('ans') in ['1', '2', '3']))

    await callback.message.answer(
        text='''
Вы вернулись к основному меню. Чем еще можем помочь?

Сіз басты бетке оралдыңыз. Тағы қандай көмек көрсете аламыз?
''',
        reply_markup=btns
    )
    await state.update_data(items=items)
    await FaqState.start.set()



import datetime

from aiogram.types.message import Message, ContentType
from aiogram.types.callback_query import CallbackQuery
from aiogram.dispatcher.storage import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from service.tgbot.models.database.users import Client, ClientsApp
from service.tgbot.keyboards.client.faq import get_times, get_grade_btns
from service.tgbot.misc.states.client import FaqState
from service.tgbot.misc.delete import remove
from service.tgbot.handlers.client.faq.main import faq_lvl_handler
from service.tgbot.lib.bitrixAPI.leads import Leads


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
    callback_data['lvl'] = 'main'
    waiting_time = callback_data.get('time')
    now_date = datetime.datetime.now()
    date = now_date + datetime.timedelta(minutes=int(waiting_time))
    data = await state.get_data()
    if not data.get('tag'):
        data['tag'] = '[LIST][619][VALUE]'
    text = '''
Вы уже подавали заявку, подождите пока оператор ответит на ваш запрос

Сіз өтініш жібердіңіз, оператор сұрауыңызға жауап бергенше күтіңіз
'''
    if not (c := await ClientsApp.get_last_app(
        session=session,
        telegram_id=user.id
    )):
        text = '''
Спасибо за выбор! Оператор свяжется с вами в указанное время.

Таңдағаныңыз үшін рақмет! Оператор сізбен көрсетілген уақытта хабарласады.
        '''
        resp = await Leads(
            user_id=callback.bot.get('config').bitrix.user_id,
            basic_token=callback.bot.get('config').bitrix.token
        ).create(
            fields={
                "FIELDS[TITLE]": "Заявка с Telegram",
                "FIELDS[NAME]": user.name,
                "FIELDS[PHONE][0][VALUE]": user.phone_number,
                "FIELDS[PHONE][0][VALUE_TYPE]": "WORKMOBILE",
                "FIELDS[UF_CRM_1733080465]": user.id,
                "FIELDS[UF_CRM_1733197853]": now_date.strftime("%d.%m.%Y %H:%M:%S"),
                "FIELDS[UF_CRM_1733197875]": date.strftime("%d.%m.%Y %H:%M:%S"),
                "FIELDS[UF_CRM_1731574397751]": data.get('tag'),
                "FIELDS[IM][0][VALUE]": "Telegram",
                "FIELDS[IM][0][VALUE_TYPE]": "Telegram",
                "FIELDS[BIRTHDATE]": user.birthday_date.strftime("%d.%m.%Y %H:%M:%S")
            }
        )
        c = ClientsApp(
            id=resp.get('result'),
            telegram_id=user.id,
            waiting_time=date,
            phone_number=user.phone_number
        )
        session.add(c)
        await session.commit()
    text += '''
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
    callback_data['lvl'] = 'main'
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
    text = texts.get(callback_data.get('ans') in ['1', '2', '3'])
    text += '''
Вы вернулись к основному меню. Чем еще можем помочь?

Сіз басты бетке оралдыңыз. Тағы қандай көмек көрсете аламыз?
'''
    await faq_lvl_handler(
        callback=callback,
        callback_data=callback_data,
        state=state,
        text=text
    )

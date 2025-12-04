import typing
import asyncio
import logging
from datetime import datetime, timedelta

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select, extract, not_, null, Date, func, True_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker, joinedload

from service.API.infrastructure.database.models import User
from service.tgbot.keyboards.auth import get_continue_btn
from service.tgbot.keyboards.client.faq import get_answer


async def push_staff_about_dismissal(
        pool: sessionmaker,
        bot: Bot,
):
    logging.info("Уведомление для сотрудников, которые уволились")
    session: AsyncSession = pool()
    now = datetime.now()
    logging.info("Уведомление для сотрудников, которые уволились")
    session: AsyncSession = pool()
    now = datetime.now()

    # - OLD (Полностью нерабочий запрос)
    # response = await session.execute(select(User).where(
    #     (func.cast(User.date_dismissal, Date) <= now.date()) &
    #     (User.is_active.is_(True))
    # ))

    # + NEW (Корректный запрос с JOIN)
    stmt = select(User).options(joinedload(User.profile)).join(UserProfile).where(
        (func.cast(UserProfile.date_dismissal, Date) <= now.date()) &
        (UserProfile.is_active == True)
    )
    response = await session.execute(stmt)
    
    users: typing.Optional[typing.List[User], None] = response.scalars().all()
    texts = {
        'rus': '''
🔄 *Изменение вашего статуса* 🔄

Мы заметили, что ваш статус в компании изменился.

💙 Если вы завершили работу в компании, *благодарим вас за ваш вклад и желаем успехов в новых начинаниях!* 🌟

🔄 Если у вас был перевод в другое юридическое лицо, необходимо перезапустить бота, чтобы обновить доступ:\
1️⃣ Остановите и заблокируйте бот (перейдите в настройки и нажмите нужную кнопку)\
2️⃣ Далее перезапустите бот\
3️⃣ Бот запросит ввести ИИН, пройдите авторизацию''',
        'kaz': '''
🔄 *Сіздің мәртебеңіздің өзгеруі* 🔄  

Біз сіздің компаниядағы мәртебеңіздің өзгергенін байқадық.  

💙 Егер сіз компаниядағы жұмысыңызды аяқтасаңыз, *сіздің үлесіңіз үшін алғысымызды білдіреміз және жаңа бастамаларыңызда сәттілік тілейміз!* 🌟  

🔄 Егер сіз басқа заңды тұлғаға ауыстырылған болсаңыз, қолжетімділікті жаңарту үшін ботты қайта іске қосу қажет:  
1️⃣ Ботты тоқтатыңыз және бұғаттаңыз (параметрлерге өтіп, тиісті батырманы басыңыз)  
2️⃣ Содан кейін ботты қайта іске қосыңыз  
3️⃣ Бот сізден ЖСН енгізуді сұрайды, авторизациядан өтіңіз
    '''
    }
    for u in users:
        # + NEW: Проверяем, что профиль загружен
        if not u.profile:
            continue

        logging.info(f'IIN -> {u.profile.iin}')
        
        # - OLD
        # u.iin = None
        # u.is_active = False
        
        # + NEW: Обновляем профиль
        u.profile.is_active = False
        
        try:
            # - OLD
            # text=texts.get(u.local if u.local else 'rus')
            # + NEW
            await bot.send_message(
                chat_id=u.id,
                text=texts.get(u.profile.local if u.profile.local else 'rus')
            )
        except Exception as ex:
            logging.info(ex)
            print(ex)
        
        session.add(u.profile) # Добавляем измененный профиль в сессию
    
    await session.commit()
    await session.close()



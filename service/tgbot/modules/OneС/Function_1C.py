from datetime import datetime

from aiogram import Bot, Dispatcher

from service.tgbot.modules.OneС.OneC import OneC, TYPES, REQUESTS
from service.tgbot.models.database.users import User, Client

from sqlalchemy.ext.asyncio import AsyncSession


async def authorization(
        user: Client,
        bot: Bot
):
    try:
        date = user.birthday_date.isoformat()
    except:
        date = user.birthday_date
    if not isinstance(user.gender, str):
        gender = user.gender.decode("utf-8")
    else:
        gender = user.gender
    js = {"phone": user.phone_number,
          "clientFullName": user.name,
          "user_tlg_id": user.id,
          "qr": True,
          "birthDate": date,
          "gender": gender}
    resp = await OneC.get_answer(
        request=REQUESTS.AUTHORIZATION,
        type_request=TYPES.POST,
        obj=bot,
        json_data=js
    )
    if resp:
        return True

    return False


async def get_balance(
        user: Client,
        bot: Bot
):
    msg = ""
    if (resp := await OneC.get_answer(
            request=REQUESTS.BALANCE + str(user.phone_number),
            type_request=TYPES.GET,
            obj=bot,
    )):
        for row in resp["dayOfLastUse"]:
            msg += "\n🔥" + str(row['date']) + " будет списано " + str(row['sum']) + " бонусов (автоматическое сгорание)"
    if resp:
        return resp.get('balance'), msg
    return 0, ""


async def bonus_accrual(
        user: Client,
        bot: Bot,
        amount: int
) -> bool:
    data = {
        'phone': user.phone_number,
        'amount': amount,
        'bonusProgram': "757c2519-811d-11ee-9876-a8a1590d610e"
    }
    if (resp := await OneC.get_answer(
        request=REQUESTS.BALANCE,
        type_request=TYPES.POST,
        obj=bot,
        json_data=data
    )):
        if resp.get('status') == 'ok':
            return True
        else:
            return False

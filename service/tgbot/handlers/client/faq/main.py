from aiogram.types.message import Message
from aiogram.types.callback_query import CallbackQuery
from aiogram.dispatcher.storage import FSMContext

from service.tgbot.keyboards.client.faq import get_faq_btns
from service.tgbot.data.faq_new import faq_texts_update, tags
from service.tgbot.misc.states.client import FaqState
from service.tgbot.models.database.users import Client
from service.tgbot.keyboards.staff import staff
from sqlalchemy.ext.asyncio import AsyncSession


async def get_faq_main_handler(
        message: Message,
        state: FSMContext
):
    _ = message.bot.get("i18n")
    await state.finish()
    btns = await get_faq_btns('main', _)
    await message.answer(
        text=_("Выберите раздел"),
        reply_markup=btns
    )


async def faq_lvl_handler(
        callback: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
        text: str = None
):
    _ = callback.bot.get("i18n")
    await state.finish()
    if not text:
        lvl = callback_data.get('lvl').replace('*', callback_data.get('chapter'))
        text = _(faq_texts_update.get(lvl) if faq_texts_update.get(lvl) else "Выберите раздел")
        if 'operator' in callback_data.get('lvl'):
            text = _(faq_texts_update.get('operator'))
            await state.update_data(tag=tags.get(callback_data.get('chapter')))
            await FaqState.waiting_operator.set()

    await callback.message.edit_text(
        text=text,
        reply_markup=await get_faq_btns(callback_data.get('lvl'), _)
    )


async def choose_locale_handler(
        callback: CallbackQuery,
        user: Client,
        state: FSMContext
):
    _ = callback.bot.get('i18n')
    text = _("Выберите язык")

    await callback.message.edit_text(
        text=text,
        reply_markup=await staff.change_locale('client_locale')
    )


async def change_locale_handler(
        query: CallbackQuery,
        user: Client,
        session: AsyncSession,
        callback_data: dict
):
    _ = query.bot.get('i18n')
    local = callback_data.get('lang')
    user.local = local
    await user.save(session)
    text = _('Вы сменили язык', locale=user.local)
    await query.message.delete()
    btns = await get_faq_btns('main', _, user.local)
    await query.message.answer(
        text=text,
        reply_markup=btns
    )

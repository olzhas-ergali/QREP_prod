from aiogram.types.message import Message
from aiogram.types.callback_query import CallbackQuery
from aiogram.dispatcher.storage import FSMContext

from service.tgbot.keyboards.client.faq import get_faq_btns
from service.tgbot.data.faq import faq_texts_update, tags
from service.tgbot.misc.states.client import FaqState


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
    callback_data.get('lvl')
    await callback.message.edit_text(
        text=text,
        reply_markup=await get_faq_btns(callback_data.get('lvl'), _)
    )


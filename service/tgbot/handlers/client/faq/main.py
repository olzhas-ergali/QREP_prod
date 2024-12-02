from aiogram.types.message import Message
from aiogram.types.callback_query import CallbackQuery
from aiogram.dispatcher.storage import FSMContext

from service.tgbot.keyboards.client.faq import get_faq_btns
from service.tgbot.data.faq import faq_texts_update
from service.tgbot.misc.states.client import FaqState


async def get_faq_main_handler(
        message: Message,
        state: FSMContext
):
    await state.finish()
    btns = await get_faq_btns('main')
    await message.answer(
        text="Выберите раздел",
        reply_markup=btns
    )


async def faq_lvl_handler(
        callback: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
        text: str = None
):
    await state.finish()
    if not text:
        lvl = callback_data.get('lvl').replace('*', callback_data.get('chapter'))
        text = faq_texts_update.get(lvl) if faq_texts_update.get(lvl) else "Выберите раздел"
        if 'operator' in callback_data.get('lvl'):
            text = faq_texts_update.get('operator')
            await FaqState.waiting_operator.set()

    await callback.message.edit_text(
        text=text,
        reply_markup=await get_faq_btns(callback_data.get('lvl'))
    )


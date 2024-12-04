import asyncio
import typing
from dataclasses import dataclass
from pathlib import Path

from aiogram import Bot, types
from aiogram.types import InputFile
from sqlalchemy.ext.asyncio import AsyncSession

from service.tgbot.misc.delete import remove
from service.tgbot.models.database.probation_period import ProbationPeriodAnswer


class FinishProbationEvent(ValueError):
    pass




@dataclass
class ProbationMedia:
    file_path: Path
    content_type: str



@dataclass
class ProbationMessageEvent:
    text: str
    media: typing.Optional[ProbationMedia] = None
    is_next: bool = False  # Если True, то мы переходим следующему евенту, не дожидаясь ответа от пользователя


class ProbationEvents:

    def __init__(
            self,
            bot: Bot,
            user_id: int,
            session: AsyncSession,
            events: typing.List[ProbationMessageEvent],
            current_day: int
    ):

        self.bot = bot
        self.events = events
        self.current_day = current_day
        self.session = session
        self.user_id = user_id

    async def _save_answer(
            self,
            current_event: ProbationMessageEvent,
            current_answer: str
    ):

        await ProbationPeriodAnswer(
            user_id=self.user_id,
            day=self.current_day,
            question=current_event.text,
            answer=current_answer
        ).save(session=self.session)

    async def send_message(
            self,
            current_event: ProbationMessageEvent
    ):

        if current_event.media is None:
            return await self.bot.send_message(
                chat_id=self.user_id,
                text=current_event.text
            )

        event_media: ProbationMedia = current_event.media


        msg = await self.bot.send_message(
            chat_id=self.user_id,
            text="Отправляем файл..."
        )

        if event_media.content_type in types.ContentTypes.PHOTO:

            await self.bot.send_photo(
                chat_id=self.user_id,
                photo=InputFile(event_media.file_path, event_media.file_path.name),
                caption=current_event.text
            )

        elif event_media.content_type in types.ContentTypes.DOCUMENT:

            await self.bot.send_document(
                chat_id=self.user_id,
                document=InputFile(event_media.file_path, event_media.file_path.name),
                caption=current_event.text
            )
        await remove(message=msg, step=0)

    async def start(
            self,
            active_stage_id=0,
            current_stage_answer: typing.Optional[str] = None
    ):


        max_stages = len(self.events)

        if max_stages - 1 < active_stage_id:
            raise FinishProbationEvent("Закончились сообщения")

        if current_stage_answer is not None and active_stage_id is not None:
            current_event = self.events[active_stage_id]
            await self._save_answer(
                current_event=current_event,
                current_answer=current_stage_answer
            )



        current_event = self.events[active_stage_id]
        await self.send_message(
            current_event=current_event
        )

        next_stage_id = active_stage_id + 1





        if current_event.is_next:
            await asyncio.sleep(0.3)
            return await self.start(
                active_stage_id=next_stage_id
            )

        return next_stage_id

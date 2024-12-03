import asyncio
import typing
from dataclasses import dataclass

from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from service.tgbot.models.database.probation_period import ProbationPeriodAnswer


class FinishProbationEvent(ValueError):
    pass


@dataclass
class ProbationMessageEvent:
    text: str
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

    async def start(
            self,
            current_stage_id: int = 0,
            current_stage_answer: typing.Optional[str] = None
    ):


        max_stages = len(self.events)

        if current_stage_answer is not None:
            current_event = self.events[current_stage_id]
            await self._save_answer(
                current_event=current_event,
                current_answer=current_stage_answer
            )
        next_stage_id = current_stage_id + 1
        if max_stages - 1 > next_stage_id:
            raise FinishProbationEvent("Закончились сообщения")

        next_event = self.events[next_stage_id]

        await self.bot.send_message(
            chat_id=self.user_id,
            text=next_event.text
        )

        if next_event.is_next:
            await asyncio.sleep(0.3)
            await self.start(
                current_stage_id=next_stage_id
            )

        return next_stage_id

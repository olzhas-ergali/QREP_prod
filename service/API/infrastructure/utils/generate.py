import datetime
import logging
import random
import string
import time
import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from service.API.infrastructure.database.cods import Cods
from service.API.infrastructure.database.checks import PromoCheckParticipation, PromoContests


class ExceptionGenerateCode(ValueError):
    pass


async def generate_code(
        session: AsyncSession,
        phone_number: str
):
    end_time = time.time() + 30

    while time.time() < end_time:

        try:
            unique_code = "".join(random.choices(string.digits, k=6))
            code_model = Cods(
                code=unique_code,
                phone_number=phone_number,
                created_at=datetime.datetime.now()
            )
            session.add(code_model)
            await session.commit()
            return code_model
        except IntegrityError as e:
            logging.info(
                f"Не получилось создать: {e}"
            )

    raise ExceptionGenerateCode(
        "Не получилось сгенерировать промокод"
    )


async def generate_promo_code(
        session: AsyncSession,
        client_id: int,
        purchase_id: str,
        price: float,
        promo_id: int
):
    end_time = time.time() + 30

    while time.time() < end_time:

        try:
            unique_code = "".join(random.choices(string.digits, k=6))
            code_model = PromoCheckParticipation(
                participation_id=uuid.uuid4(),
                participation_number="QR2025-" + unique_code,
                promo_id=promo_id,
                check_id=purchase_id,
                client_id=client_id,
                amount_initial=price,
                amount_effective=price
            )
            session.add(code_model)
            await session.commit()
            return code_model
        except IntegrityError as e:
            logging.info(
                f"Не получилось создать: {e}"
            )

    raise ExceptionGenerateCode(
        "Не получилось сгенерировать промокод"
    )


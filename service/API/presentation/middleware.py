# @app.middleware('http')
import logging
import time

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from service.API.infrastructure.database.session import get_session, db_session

REQUEST_SLOW_THRESHOLD_SEC = 3.0


async def db_session_middleware(request: Request, call_next):
    session: AsyncSession = await get_session()
    token = db_session.set(session)
    start = time.perf_counter()
    try:
        response = await call_next(request)
        return response
    except Exception:
        await session.rollback()
        raise
    finally:
        elapsed = time.perf_counter() - start
        if elapsed >= REQUEST_SLOW_THRESHOLD_SEC:
            logging.warning(
                "Slow request: %s %s %.2fs",
                request.method,
                request.url.path,
                elapsed,
            )
        db_session.reset(token)
        await session.close()

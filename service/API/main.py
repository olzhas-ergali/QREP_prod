import logging
from http.client import HTTPException

from fastapi import FastAPI
from loguru import logger
from starlette.responses import JSONResponse

from service.API.config import settings
from service.API import application
from service.API.infrastructure.database.models import Base
from service.API.infrastructure.database.session import engine
from service.API.presentation import rest, middleware

# Adjust the logging
# -------------------------------

logging.basicConfig(
    level=logging.INFO,
    format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
)
logger.add(
    "".join(
        [
            str(settings.root_dir),
            "/logs/",
            settings.logging.file.lower(),
            ".log",
        ]
    ),
    format=settings.logging.format,
    rotation=settings.logging.rotation,
    compression=settings.logging.compression,
    level="INFO",
)

# Adjust the application
# -------------------------------
app: FastAPI = application.create(
    debug=settings.debug_status,
    rest_routers=(
        rest.purchases.router,
        rest.staff.router,
        rest.client.router
    ),
    middlewares=(
        middleware.db_session_middleware,
    ),
    startup_tasks=[],
    shutdown_tasks=[],
    docs_url="/docs", redoc_url=None
)


@app.on_event('startup')
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "Internal Server Error"}
    )

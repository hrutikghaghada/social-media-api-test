import logging
from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_tables, database
from app.logging_conf import configure_logging
from app.routes.like import router as like_router
from app.routes.post import router as post_router
from app.routes.user import router as user_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    await database.connect()
    await create_tables()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan, title="Social Media API")

app.add_middleware(CorrelationIdMiddleware)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(post_router)
app.include_router(user_router)
app.include_router(like_router)


@app.get("/health", status_code=200, tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "social_media_api"}


@app.exception_handler(HTTPException)
async def http_exception_handle_logging(request, exc):
    logger.error(f"HTTPException: {exc.status_code} {exc.detail}")
    return await http_exception_handler(request, exc)

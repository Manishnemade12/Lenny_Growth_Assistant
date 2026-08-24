"""FastAPI application entry point registering all routes including artifacts."""

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pythonjsonlogger import json as json_logger

from app.agent.providers.factory import initialize_providers
from app.api.middleware.error_handler import global_exception_handler
from app.api.middleware.logging import StructuredLoggingMiddleware
from app.api.routes import artifacts, chat, config, health, sessions
from app.config import settings
from app.db.database import close_db, init_db
from app.rag.ingestion import verify_knowledge_base


def _configure_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    formatter = json_logger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        rename_fields={"asctime": "timestamp", "levelname": "level", "name": "logger"},
    )
    handler.setFormatter(formatter)
    root_logger = logging.getLogger("app")
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    root_logger.addHandler(handler)
    root_logger.propagate = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    _configure_logging()
    logger = logging.getLogger("app.main")

    logger.info("Starting Lenny Growth Assistant", extra={"llm_provider": settings.ACTIVE_LLM_PROVIDER})
    await init_db()
    await initialize_providers()
    await verify_knowledge_base()

    yield

    await close_db()
    logger.info("Lenny Growth Assistant shut down")


app = FastAPI(
    title="Lenny Growth Assistant API",
    description="Grounded AI Conversational Assistant for Lenny's Podcast Transcripts",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(StructuredLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(Exception, global_exception_handler)

app.include_router(health.router, tags=["Health"])
app.include_router(sessions.router, prefix="/api", tags=["Sessions"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(artifacts.router, prefix="/api", tags=["Artifacts"])
app.include_router(config.router, prefix="/api", tags=["Configuration"])

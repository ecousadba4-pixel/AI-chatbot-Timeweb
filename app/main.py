from __future__ import annotations
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import get_settings
from app.services.timeweb_agent import timeweb_agent_client

settings = get_settings()


# === Жизненный цикл приложения ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with timeweb_agent_client(settings) as agent:
        app.state.timeweb_agent = agent
        yield


# === Инициализация приложения ===
app = FastAPI(
    title="TimeWeb AI ChatBot",
    version="0.1.0",
    lifespan=lifespan
)

# === CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Маршруты приложения ===
app.include_router(router)


# === Базовый корень API ===
@app.get("/", include_in_schema=False)
def root() -> dict:
    """Проверка корня API."""
    return {"service": "timeweb-ai-chatbot", "env": settings.app_env}


# === Healthcheck для балансировщика ===
@app.get("/health", include_in_schema=False)
def health() -> dict:
    """Минимальный эндпоинт для проверки доступности приложения."""
    return {"status": "ok"}


# === Дополнительная проверка готовности (опционально) ===
@app.get("/ready", include_in_schema=False)
async def ready() -> dict:
    """Проверка, инициализирован ли timeweb_agent."""
    ok = hasattr(app.state, "timeweb_agent") and app.state.timeweb_agent is not None
    return {"ready": ok}

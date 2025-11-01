from __future__ import annotations
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import get_settings
from app.services.timeweb_agent import timeweb_agent_client

log = logging.getLogger("uvicorn.error")

# Настройки могут бросать ValidationError, поэтому оборачиваем
try:
    settings = get_settings()
except Exception as e:
    # Не роняем приложение — логируем и работаем в деградирующем режиме
    log.exception("Failed to load settings: %s", e)
    settings = None  # дальше обработаем в эндпоинтах


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.timeweb_agent = None
    if settings is None:
        # настроек нет — запускаемся без агента
        yield
        return

    # Пытаемся инициализировать клиента агента, но не падаем при ошибке
    try:
        async with timeweb_agent_client(settings) as agent:
            app.state.timeweb_agent = agent
            yield
    except Exception as e:
        log.exception("Failed to init timeweb_agent: %s", e)
        # всё равно поднимаем сервис, чтобы healthcheck проходил
        yield


app = FastAPI(
    title="TimeWeb AI ChatBot",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Роутер можно подключить даже в деградирующем режиме —
# эндпоинты внутри уже должны корректно обрабатывать отсутствие агента.
app.include_router(router)


@app.get("/", include_in_schema=False)
def root() -> dict:
    env = getattr(settings, "app_env", "unknown") if settings else "no-settings"
    return {"service": "timeweb-ai-chatbot", "env": env}


@app.get("/health", include_in_schema=False)
def health() -> dict:
    """Лёгкая проверка живости процесса."""
    return {"status": "ok"}


@app.get("/ready", include_in_schema=False)
def ready() -> dict:
    """Проверка  готовности зависимостей (не обязательно для 200 на /health)."""
    has_settings = settings is not None
    has_agent = getattr(app.state, "timeweb_agent", None) is not None
    return {"settings": has_settings, "agent": has_agent}


from __future__ import annotations
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response, JSONResponse

from app.api.routes import router
from app.core.config import get_settings
from app.services.timeweb_agent import timeweb_agent_client

log = logging.getLogger("uvicorn.error")

# Безопасная загрузка настроек
try:
    settings = get_settings()
except Exception as e:
    log.exception("Failed to load settings: %s", e)
    settings = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.timeweb_agent = None
    if settings is None:
        yield
        return

    try:
        async with timeweb_agent_client(settings) as agent:
            app.state.timeweb_agent = agent
            yield
    except Exception as e:
        log.exception("Failed to init timeweb_agent: %s", e)
        yield


app = FastAPI(title="TimeWeb AI ChatBot", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем основной роутер
app.include_router(router)

# --- Корневые эндпоинты и healthchecks ---

@app.get("/", include_in_schema=False)
def root_get() -> JSONResponse:
    env = getattr(settings, "app_env", "unknown") if settings else "no-settings"
    return JSONResponse({"service": "timeweb-ai-chatbot", "env": env})

@app.head("/", include_in_schema=False)
def root_head() -> Response:
    # Явно отвечаем 200 на HEAD / для балансировщика
    return Response(status_code=200)


@app.get("/health", include_in_schema=False)
def health_get() -> JSONResponse:
    return JSONResponse({"status": "ok"})

@app.head("/health", include_in_schema=False)
def health_head() -> Response:
    return Response(status_code=200)


@app.get("/ready", include_in_schema=False)
def ready_get() -> JSONResponse:
    has_settings = settings is not None
    has_agent = getattr(app.state, "timeweb_agent", None) is not None
    return JSONResponse({"settings": has_settings, "agent": has_agent})



from __future__ import annotations
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import get_settings
from app.services.timeweb_agent import timeweb_agent_client

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with timeweb_agent_client(settings) as agent:
        app.state.timeweb_agent = agent
        yield


app = FastAPI(title="TimeWeb AI ChatBot", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root() -> dict:
    """Базовый корень API."""

    return {"service": "timeweb-ai-chatbot", "env": settings.app_env}

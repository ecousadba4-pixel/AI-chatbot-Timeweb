"""Минимальная заглушка pydantic-settings."""
from __future__ import annotations

import os
from typing import Any, Dict

from pydantic import BaseModel


class BaseSettings(BaseModel):
    """Читает значения из переменных окружения по alias из Field."""

    def __init__(self, **data: Any) -> None:
        env_data: Dict[str, Any] = {}
        for name, info in self.__class__.__fields__.items():
            alias = info.alias or name
            if alias in os.environ:
                env_data[name] = os.environ[alias]
        env_data.update(data)
        super().__init__(**env_data)


__all__ = ["BaseSettings"]

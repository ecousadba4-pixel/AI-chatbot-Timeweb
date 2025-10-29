"""Минимальные заглушки для pydantic, необходимые в тестах."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict


@dataclass
class FieldInfo:
    default: Any = ...
    default_factory: Callable[[], Any] | None = None
    alias: str | None = None
    description: str | None = None
    annotation: Any | None = None


def Field(
    *,
    default: Any = ...,  # noqa: ANN401
    default_factory: Callable[[], Any] | None = None,
    alias: str | None = None,
    description: str | None = None,
) -> FieldInfo:
    """Возвращает объект с метаданными поля."""

    return FieldInfo(
        default=default,
        default_factory=default_factory,
        alias=alias,
        description=description,
    )


class _BaseModelMeta(type):
    def __new__(mcls, name: str, bases: tuple[type, ...], namespace: Dict[str, Any]):
        cls = super().__new__(mcls, name, bases, dict(namespace))
        annotations: Dict[str, Any] = {}
        for base in reversed(bases):
            annotations.update(getattr(base, "__annotations__", {}))
        annotations.update(namespace.get("__annotations__", {}))

        fields: Dict[str, FieldInfo] = {}
        for attr, annotation in annotations.items():
            if attr.startswith("_"):
                continue
            value = namespace.get(attr, getattr(cls, attr, ...))
            if isinstance(value, FieldInfo):
                info = value
            else:
                info = Field(default=value)
            info.annotation = annotation
            fields[attr] = info
            if info.default is not ...:
                setattr(cls, attr, info.default)
            elif info.default_factory is not None:
                setattr(cls, attr, info.default_factory())
        cls.__fields__ = fields
        return cls


class ValidationError(Exception):
    """Исключение для совместимости с pydantic."""


class BaseModel(metaclass=_BaseModelMeta):
    __fields__: Dict[str, FieldInfo]

    def __init__(self, **data: Any) -> None:
        values: Dict[str, Any] = {}
        for name, info in self.__class__.__fields__.items():
            alias = info.alias or name
            if name in data:
                raw = data[name]
            elif alias in data:
                raw = data[alias]
            elif info.default is not ...:
                raw = info.default
            elif info.default_factory is not None:
                raw = info.default_factory()
            else:
                raise ValidationError(f"Field '{name}' is required")
            values[name] = _convert(raw, info.annotation)
        for key, value in values.items():
            setattr(self, key, value)

    def dict(self) -> Dict[str, Any]:
        return {name: getattr(self, name) for name in self.__class__.__fields__}


def _convert(value: Any, annotation: Any | None) -> Any:
    if annotation in (str, None):
        return str(value) if annotation is str and not isinstance(value, str) else value
    if annotation is int:
        return int(value)
    if annotation is float:
        return float(value)
    if annotation is bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "on"}
        return bool(value)
    return value


AnyHttpUrl = str


__all__ = [
    "AnyHttpUrl",
    "BaseModel",
    "Field",
    "ValidationError",
]

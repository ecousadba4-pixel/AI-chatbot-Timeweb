from __future__ import annotations

import asyncio

import pytest


@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem: pytest.Function) -> bool | None:
    """Поддержка запуска async-тестов без сторонних плагинов.

    Pytest без дополнительных плагинов не умеет выполнять ``async def`` тесты.
    В наших тестах используется метка ``@pytest.mark.anyio`` с указанием
    бэкенда ``"asyncio"``. Чтобы не добавлять внешнюю зависимость, реализуем
    минимальную обвязку, которая запускает такие корутины через ``asyncio.run``.
    """

    markers = {mark.name for mark in pyfuncitem.iter_markers()}
    if "anyio" not in markers:
        return None

    test_func = pyfuncitem.obj
    if not asyncio.iscoroutinefunction(test_func):
        return None

    backend = pyfuncitem.funcargs.get("anyio_backend", "asyncio")
    if backend != "asyncio":  # pragma: no cover - в тестах используется только asyncio
        raise RuntimeError(f"Unsupported AnyIO backend: {backend}")

    asyncio.run(test_func(**pyfuncitem.funcargs))
    return True

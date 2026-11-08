"""Задание 6 (средняя сложность): FastAPI «Hello».

Минимальное FastAPI-приложение: корневой endpoint возвращает JSON-
приветствие, /hello/{name} - персональное, /health - проверка живости.
Автодокументация Swagger доступна на /docs.

Запуск:
    uvicorn task06_fastapi_hello:app --port 5006
    # открыть http://127.0.0.1:5006/ или /docs
"""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title="Hello API", description="Задание 6: FastAPI Hello")


@app.get("/")
def read_root() -> dict[str, str]:
    """Корневой endpoint: приветствие в JSON."""
    return {"message": "Hello, FastAPI!"}


@app.get("/hello/{name}")
def read_hello(name: str) -> dict[str, str]:
    """Персональное приветствие по имени из пути."""
    return {"message": f"Привет, {name}!"}


@app.get("/health")
def read_health() -> dict[str, str]:
    """Технический endpoint проверки живости сервиса."""
    return {"status": "ok"}

"""Собирает demo_output.txt: живые HTTP-запросы, тесты и flake8.

Поднимает Flask/FastAPI серверы на локальных портах, выполняет реальные
HTTP-запросы через httpx и гасит серверы. Никаких фоновых процессов
после завершения не остаётся.
"""

from __future__ import annotations

import datetime
import subprocess
import sys
import time

import httpx

SEP = "-" * 70
out = []
out.append("Лабораторная работа №6, вариант 4 - фактические запуски")
out.append("=" * 70)
out.append("")
out.append("Дата выполнения: " + datetime.date.today().strftime("%d.%m.%Y"))
out.append("Python: 3.11.1, Flask 3.1, FastAPI 0.162, SQLAlchemy 2.1")
out.append("ОС: Windows 10")
out.append("")
out.append("Для каждого веб-приложения поднимался реальный сервер")
out.append("(Flask dev server / uvicorn), запросы выполнены через httpx,")
out.append("после чего сервер остановлен. Ниже команды, HTTP-статусы")
out.append("и тела ответов.")
out.append("")


def log(text: str = "") -> None:
    out.append(text)


def section(title: str) -> None:
    log(SEP)
    log(title)
    log(SEP)


def show(method: str, url: str, **kwargs) -> httpx.Response:
    """Выполняет запрос и записывает статус и тело в протокол."""
    response = httpx.request(method, url, timeout=10, **kwargs)
    log(f"$ {method} {url}")
    if "json" in kwargs:
        log(f"  тело запроса: {kwargs['json']}")
    log(f"HTTP {response.status_code}")
    text = response.text
    log(text[:1500] + ("\n...[обрезано]" if len(text) > 1500 else ""))
    log()
    return response


class Server:
    """Контекст: поднять сервер и гарантированно остановить."""

    def __init__(self, cmd: list[str], ready_url: str) -> None:
        self.cmd = cmd
        self.ready_url = ready_url
        self.process = None

    def __enter__(self) -> None:
        log(f"$ {' '.join(self.cmd)}")
        self.process = subprocess.Popen(
            self.cmd, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)
        for _ in range(60):
            try:
                httpx.get(self.ready_url, timeout=1)
                return
            except httpx.HTTPError:
                time.sleep(0.5)
        raise RuntimeError(f"сервер не поднялся: {self.ready_url}")

    def __exit__(self, *args) -> None:
        self.process.terminate()
        self.process.wait(timeout=10)


def demo_flask() -> None:
    section("Задание 4 (средняя). Flask: страница с таблицей")
    with Server([sys.executable, "task04_flask_table.py"],
                "http://127.0.0.1:5004/api/students"):
        show("GET", "http://127.0.0.1:5004/")
        show("GET", "http://127.0.0.1:5004/api/students")
    log("сервер остановлен")
    log()


def demo_hello() -> None:
    section("Задание 6 (средняя). FastAPI Hello")
    with Server([sys.executable, "-m", "uvicorn",
                 "task06_fastapi_hello:app", "--port", "5006"],
                "http://127.0.0.1:5006/health"):
        show("GET", "http://127.0.0.1:5006/")
        show("GET", "http://127.0.0.1:5006/hello/Ярослав")
    log("сервер остановлен")
    log()


def demo_tasks() -> None:
    section("Задание 10 (средняя). REST API списка задач")
    with Server([sys.executable, "-m", "uvicorn",
                 "task10_rest_tasks:app", "--port", "5010"],
                "http://127.0.0.1:5010/tasks"):
        show("POST", "http://127.0.0.1:5010/tasks",
             json={"title": "Сдать лабу №6"})
        show("POST", "http://127.0.0.1:5010/tasks",
             json={"title": "Проверить ответ бота"})
        show("GET", "http://127.0.0.1:5010/tasks")
        show("PATCH", "http://127.0.0.1:5010/tasks/1",
             json={"done": True})
        show("DELETE", "http://127.0.0.1:5010/tasks/2")
        show("GET", "http://127.0.0.1:5010/tasks/999")
    log("сервер остановлен")
    log()


def demo_notes() -> None:
    section("Задание 5 (повышенная). REST API заметок")
    with Server([sys.executable, "-m", "uvicorn",
                 "task05_notes_api:app", "--port", "5005"],
                "http://127.0.0.1:5005/notes"):
        show("POST", "http://127.0.0.1:5005/notes",
             json={"title": "Flask", "content": "Шаблоны Jinja2",
                   "tags": ["учёба"]})
        show("POST", "http://127.0.0.1:5005/notes",
             json={"title": "FastAPI", "content": "Swagger на /docs",
                   "tags": ["учёба", "api"]})
        show("GET", "http://127.0.0.1:5005/notes?tag=api")
        show("GET", "http://127.0.0.1:5005/notes?q=jinja")
        show("PUT", "http://127.0.0.1:5005/notes/1",
             json={"title": "Flask 3", "content": "Обновлённый текст"})
        show("DELETE", "http://127.0.0.1:5005/notes/2")
        show("GET", "http://127.0.0.1:5005/notes")
    log("сервер остановлен")
    log()


def demo_simple(title: str, cmd: list[str]) -> None:
    section(title)
    result = subprocess.run(cmd, capture_output=True, text=True,
                            encoding="utf-8")
    log("$ " + " ".join(cmd))
    log()
    if result.stdout.strip():
        log(result.stdout.rstrip("\n"))
    if result.stderr.strip():
        log(result.stderr.rstrip("\n"))
    log()
    log(f"код возврата: {result.returncode}")
    log()


def main() -> None:
    demo_flask()
    demo_hello()
    demo_tasks()
    demo_notes()
    demo_simple("Задание 9 (повышенная). SQLAlchemy CRUD",
                [sys.executable, "task09_sqlalchemy_demo.py"])
    demo_simple("Модульные тесты всех заданий (unittest)",
                [sys.executable, "-m", "unittest", "-v"])
    demo_simple("Проверка стиля кода (flake8)",
                [sys.executable, "-m", "flake8", ".", "--statistics"])
    with open("demo_output.txt", "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write("\n".join(out).rstrip("\n") + "\n")
    print("demo_output.txt записан, строк:", len(out))


if __name__ == "__main__":
    main()

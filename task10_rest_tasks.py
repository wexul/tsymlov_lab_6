"""Задание 10 (средняя сложность): простейший REST API список задач.

FastAPI CRUD для задач (todo): список, создание, получение по id,
обновление статуса/текста, удаление. Хранилище в памяти (словарь),
валидация входа через Pydantic, 404 для несуществующих id.

Запуск:
    uvicorn task10_rest_tasks:app --port 5010
    # документация: http://127.0.0.1:5010/docs
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Tasks API", description="Задание 10: список задач")


class TaskIn(BaseModel):
    """Тело запроса на создание задачи."""

    title: str = Field(min_length=1, max_length=200)
    done: bool = False


class TaskPatch(BaseModel):
    """Тело запроса на частичное обновление задачи."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    done: bool | None = None


class Task(TaskIn):
    """Задача с идентификатором."""

    id: int


_tasks: dict[int, Task] = {}
_next_id = 1


def reset_storage() -> None:
    """Очищает хранилище (используется в тестах)."""
    global _next_id
    _tasks.clear()
    _next_id = 1


def _get_task_or_404(task_id: int) -> Task:
    """Возвращает задачу или бросает HTTP 404."""
    task = _tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404,
                            detail=f"Задача {task_id} не найдена")
    return task


@app.get("/tasks", response_model=list[Task])
def list_tasks() -> list[Task]:
    """Возвращает все задачи."""
    return list(_tasks.values())


@app.post("/tasks", response_model=Task, status_code=201)
def create_task(payload: TaskIn) -> Task:
    """Создаёт задачу и присваивает id."""
    global _next_id
    task = Task(id=_next_id, **payload.model_dump())
    _tasks[task.id] = task
    _next_id += 1
    return task


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int) -> Task:
    """Возвращает задачу по id."""
    return _get_task_or_404(task_id)


@app.patch("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, payload: TaskPatch) -> Task:
    """Обновляет переданные поля задачи."""
    task = _get_task_or_404(task_id)
    changes = payload.model_dump(exclude_unset=True)
    updated = task.model_copy(update=changes)
    _tasks[task_id] = updated
    return updated


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int) -> None:
    """Удаляет задачу; 204 No Content при успехе."""
    _get_task_or_404(task_id)
    del _tasks[task_id]

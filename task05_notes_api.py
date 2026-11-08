"""Задание 5 (повышенная сложность): REST API для заметок.

FastAPI CRUD заметок с полями title/content/tags и метками времени:
создание, чтение (список и по id), полное обновление, удаление.
Список поддерживает поиск по тексту (?q=), фильтр по тегу (?tag=)
и пагинацию (?limit=&offset=). Хранилище в памяти, ошибки 404/422
обрабатываются штатно FastAPI.

Запуск:
    uvicorn task05_notes_api:app --port 5005
    # документация: http://127.0.0.1:5005/docs
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI(title="Notes API", description="Задание 5: заметки")


class NoteIn(BaseModel):
    """Тело запроса на создание/обновление заметки."""

    title: str = Field(min_length=1, max_length=200)
    content: str = Field(default="", max_length=10_000)
    tags: list[str] = Field(default_factory=list)


class Note(NoteIn):
    """Заметка с id и метками времени."""

    id: int
    created_at: datetime
    updated_at: datetime


_notes: dict[int, Note] = {}
_next_id = 1


def reset_storage() -> None:
    """Очищает хранилище (используется в тестах)."""
    global _next_id
    _notes.clear()
    _next_id = 1


def _utc_now() -> datetime:
    """Текущее время UTC (наивная дата не используется)."""
    return datetime.now(timezone.utc)


def _get_note_or_404(note_id: int) -> Note:
    """Возвращает заметку или бросает HTTP 404."""
    note = _notes.get(note_id)
    if note is None:
        raise HTTPException(status_code=404,
                            detail=f"Заметка {note_id} не найдена")
    return note


@app.get("/notes", response_model=list[Note])
def list_notes(
    q: str | None = Query(default=None,
                          description="подстрока в заголовке/тексте"),
    tag: str | None = Query(default=None, description="фильтр по тегу"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
) -> list[Note]:
    """Список заметок с поиском, фильтром по тегу и пагинацией."""
    result = sorted(_notes.values(), key=lambda note: note.id)
    if q:
        needle = q.lower()
        result = [note for note in result
                  if needle in note.title.lower()
                  or needle in note.content.lower()]
    if tag:
        result = [note for note in result if tag in note.tags]
    return result[offset:offset + limit]


@app.post("/notes", response_model=Note, status_code=201)
def create_note(payload: NoteIn) -> Note:
    """Создаёт заметку с метками времени."""
    global _next_id
    now = _utc_now()
    note = Note(id=_next_id, created_at=now, updated_at=now,
                **payload.model_dump())
    _notes[note.id] = note
    _next_id += 1
    return note


@app.get("/notes/{note_id}", response_model=Note)
def get_note(note_id: int) -> Note:
    """Возвращает заметку по id."""
    return _get_note_or_404(note_id)


@app.put("/notes/{note_id}", response_model=Note)
def replace_note(note_id: int, payload: NoteIn) -> Note:
    """Полностью заменяет содержимое заметки, обновляет updated_at."""
    note = _get_note_or_404(note_id)
    updated = Note(id=note.id, created_at=note.created_at,
                   updated_at=_utc_now(), **payload.model_dump())
    _notes[note_id] = updated
    return updated


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int) -> None:
    """Удаляет заметку; 204 No Content при успехе."""
    _get_note_or_404(note_id)
    del _notes[note_id]

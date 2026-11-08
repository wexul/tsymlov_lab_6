Полошков Ярослав Витальевич, группа 220042-11, вариант 4, лабораторная №6

# Лабораторная работа №6. Веб-программирование на Python

Дисциплина: «Методы и технологии программирования» (часть 1).

**Цель работы:** изучить основы веб-программирования: Flask и FastAPI,
REST API, шаблоны Jinja2.

Окружение: Python 3.11.1, Windows, Flask 3.1, FastAPI 0.162 (uvicorn),
SQLAlchemy 2.1, httpx (тесты и протокол). Установка:
`pip install -r requirements.txt`.

## Задания варианта 4

По таблице индивидуальных вариантов (строка «4»: `4 6 10 | 5 9`):

| Сложность | № | Задание | Файл |
|-----------|---|---------|------|
| Средняя | 4 | Страница с таблицей данных (Flask) | [`task04_flask_table.py`](task04_flask_table.py) |
| Средняя | 6 | FastAPI «Hello» | [`task06_fastapi_hello.py`](task06_fastapi_hello.py) |
| Средняя | 10 | Простейший REST API список задач | [`task10_rest_tasks.py`](task10_rest_tasks.py) |
| Повышенная | 5 | REST API для заметок | [`task05_notes_api.py`](task05_notes_api.py) |
| Повышенная | 9 | Подключение SQLAlchemy | [`task09_sqlalchemy_demo.py`](task09_sqlalchemy_demo.py) |

Протокол [`demo_output.txt`](demo_output.txt) собран скриптом
`collect_demo.py`: для каждого веб-приложения поднимался **реальный
сервер**, запросы выполнялись через httpx (статусы и тела ответов в
протоколе), после чего сервер останавливался. Ниже — разбор решений и
выдержки.

---

## Средняя сложность

### Задание 4. Страница с таблицей данных (Flask)

Flask-приложение рендерит таблицу студентов через шаблон Jinja2
(`templates/students.html`, цикл `{% for %}`), средний балл считается
на сервере. Дополнительный endpoint `/api/students` отдаёт те же
данные в JSON. Приложение создаётся фабрикой `create_app()` — это
упрощает тестирование через `test_client`.

```
$ GET http://127.0.0.1:5004/api/students
HTTP 200
{"students":[{"group":"220042-11","grade":5,"name":"Полошков Ярослав
Витальевич"}, ...], "average": 4.25}
```

### Задание 6. FastAPI «Hello»

Три endpoint: `/` — JSON-приветствие, `/hello/{name}` — персональное
приветствие по параметру пути, `/health` — проверка живости. Swagger
автоматически доступен на `/docs` (схема `/openapi.json` проверена
тестом).

```
$ GET http://127.0.0.1:5006/
HTTP 200
{"message":"Hello, FastAPI!"}
$ GET http://127.0.0.1:5006/hello/Ярослав
HTTP 200
{"message":"Привет, Ярослав!"}
```

### Задание 10. Простейший REST API список задач

CRUD задач на FastAPI: `GET/POST /tasks`, `GET/PATCH/DELETE
/tasks/{id}`. Валидация через Pydantic (`title` обязателен, 1–200
символов), коды ответов по REST: 201 при создании, 204 при удалении,
404 для несуществующего id, 422 при невалидном теле. Хранилище —
словарь в памяти.

```
$ POST http://127.0.0.1:5010/tasks   {"title": "Сдать лабу №6"}
HTTP 201
$ PATCH http://127.0.0.1:5010/tasks/1   {"done": true}
HTTP 200
$ GET http://127.0.0.1:5010/tasks/999
HTTP 404
```

---

## Повышенная сложность

### Задание 5. REST API для заметок

CRUD заметок (title, content, tags, created_at/updated_at UTC):
`GET/POST /notes`, `GET/PUT/DELETE /notes/{id}`. Список поддерживает
**поиск** `?q=` по заголовку и тексту, **фильтр по тегу** `?tag=` и
**пагинацию** `?limit=&offset=` (с валидацией границ через Query).
PUT полностью заменяет содержимое и обновляет `updated_at`.

```
$ GET http://127.0.0.1:5005/notes?tag=api
HTTP 200   (только заметки с тегом api)
$ PUT http://127.0.0.1:5005/notes/1
HTTP 200   (title/content заменены, updated_at обновлён)
```

### Задание 9. Подключение SQLAlchemy

SQLAlchemy 2.0 ORM, декларативный стиль: модель `Student`
(`DeclarativeBase`, `Mapped`, `mapped_column`) для SQLite и CRUD-
функции (`add_student`, `get_students` с фильтром по группе,
`update_grade`, `delete_student`). Сессии открываются через
`with Session(engine)`, данные валидируются, несуществующий id даёт
`LookupError`. Демо и тесты работают на in-memory базе.

```
$ python task09_sqlalchemy_demo.py
INSERT: добавлено 3 записи
SELECT по группе 220042-11: 2 записи
UPDATE: у студента id=1 теперь оценка 4
DELETE: удалён id=1; осталось записей: 2
```

---

## Проверка качества

### Модульные тесты

```
$ py -3 -m unittest -v
...
Ran 24 tests in 0.228s

OK
```

24 теста: Flask через `test_client` (HTML таблицы и JSON), FastAPI
через `TestClient` (все CRUD-операции, 404/422, поиск, пагинация,
схема OpenAPI), SQLAlchemy на in-memory SQLite (CRUD, фильтры,
валидация, LookupError). Реальный сервер для тестов не нужен.
Полный вывод — в `demo_output.txt`.

### Соответствие PEP8

```
$ py -3 -m flake8 .
(команда не вывела ни одной строки)
код возврата: 0
```

Строки не длиннее 79 символов, docstring у каждого модуля, класса и
функции, аннотации типов, имена по `snake_case`.

## Структура репозитория

| Файл | Назначение |
|------|------------|
| `README.md` | Данные студента (первая строка) и отчёт по заданиям |
| `task04_flask_table.py` | Задание 4 (средняя): Flask + Jinja2 таблица |
| `templates/students.html` | Jinja2-шаблон таблицы студентов |
| `task06_fastapi_hello.py` | Задание 6 (средняя): FastAPI Hello |
| `task10_rest_tasks.py` | Задание 10 (средняя): REST API задач |
| `task05_notes_api.py` | Задание 5 (повышенная): REST API заметок |
| `task09_sqlalchemy_demo.py` | Задание 9 (повышенная): SQLAlchemy CRUD |
| `test_tasks.py` | 24 теста (`py -3 -m unittest -v`) |
| `demo_output.txt` | Протокол: живые HTTP-запросы, тесты, flake8 |
| `collect_demo.py` | Скрипт сбора протокола (поднимает/гасит серверы) |
| `requirements.txt` | Flask, FastAPI, uvicorn, SQLAlchemy, httpx |
| `.gitignore` | Исключения для Python-проекта и `students.db` |

## Как запустить

```bash
pip install -r requirements.txt

python task04_flask_table.py                          # :5004
uvicorn task06_fastapi_hello:app --port 5006          # :5006
uvicorn task10_rest_tasks:app --port 5010             # :5010
uvicorn task05_notes_api:app --port 5005              # :5005
python task09_sqlalchemy_demo.py

python -m unittest -v        # тесты
python -m flake8 .           # проверка стиля
python collect_demo.py       # пересобрать протокол
```

Работа велась в feature-ветках, каждая слита в `main` merge-коммитом
(`--no-ff`). Сообщения коммитов — по Conventional Commits.

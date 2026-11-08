"""Модульные тесты всех заданий лабораторной №6 (unittest).

Flask проверяется через test_client, FastAPI - через TestClient
(httpx), реальный сервер для тестов не нужен. SQLAlchemy тестируется
на in-memory базе SQLite.

Запуск: python -m unittest -v
"""

from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from task04_flask_table import STUDENTS, average_grade, create_app
from task05_notes_api import app as notes_app
from task05_notes_api import reset_storage as reset_notes
from task06_fastapi_hello import app as hello_app
from task09_sqlalchemy_demo import (
    add_student,
    delete_student,
    get_students,
    init_db,
    make_engine,
    update_grade,
)
from task10_rest_tasks import app as tasks_app
from task10_rest_tasks import reset_storage as reset_tasks


class TestFlaskTable(unittest.TestCase):
    """Задание 4: Flask-страница с таблицей."""

    def setUp(self) -> None:
        self.client = create_app().test_client()

    def test_index_contains_table(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("<table>", html)
        for student in STUDENTS:
            self.assertIn(student["name"], html)
        self.assertIn("средний балл", html)

    def test_api_students(self) -> None:
        response = self.client.get("/api/students")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data["students"]), len(STUDENTS))
        self.assertAlmostEqual(data["average"], average_grade(STUDENTS))

    def test_average_grade(self) -> None:
        self.assertIsNone(average_grade([]))
        self.assertAlmostEqual(average_grade(STUDENTS), 4.25)


class TestFastApiHello(unittest.TestCase):
    """Задание 6: FastAPI Hello."""

    def setUp(self) -> None:
        self.client = TestClient(hello_app)

    def test_root(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Hello, FastAPI!"})

    def test_hello_name(self) -> None:
        response = self.client.get("/hello/Ярослав")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Привет, Ярослав!")

    def test_health(self) -> None:
        self.assertEqual(self.client.get("/health").json(),
                         {"status": "ok"})

    def test_openapi_schema_available(self) -> None:
        response = self.client.get("/openapi.json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("/hello/{name}", response.json()["paths"])


class TestTasksApi(unittest.TestCase):
    """Задание 10: REST API списка задач."""

    def setUp(self) -> None:
        reset_tasks()
        self.client = TestClient(tasks_app)

    def test_empty_list(self) -> None:
        self.assertEqual(self.client.get("/tasks").json(), [])

    def test_create_and_get(self) -> None:
        response = self.client.post("/tasks", json={"title": "Сдать лабу"})
        self.assertEqual(response.status_code, 201)
        task = response.json()
        self.assertEqual(task["id"], 1)
        self.assertFalse(task["done"])
        fetched = self.client.get("/tasks/1")
        self.assertEqual(fetched.json()["title"], "Сдать лабу")

    def test_create_empty_title_rejected(self) -> None:
        response = self.client.post("/tasks", json={"title": ""})
        self.assertEqual(response.status_code, 422)

    def test_update(self) -> None:
        self.client.post("/tasks", json={"title": "Задача"})
        response = self.client.patch("/tasks/1", json={"done": True})
        self.assertEqual(response.json()["done"], True)
        self.assertEqual(response.json()["title"], "Задача")

    def test_delete(self) -> None:
        self.client.post("/tasks", json={"title": "Задача"})
        response = self.client.delete("/tasks/1")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.client.get("/tasks/1").status_code, 404)

    def test_missing_task_404(self) -> None:
        self.assertEqual(self.client.get("/tasks/999").status_code, 404)
        self.assertEqual(self.client.patch("/tasks/999",
                                           json={"done": True})
                         .status_code, 404)
        self.assertEqual(self.client.delete("/tasks/999").status_code,
                         404)


class TestNotesApi(unittest.TestCase):
    """Задание 5 (повышенная): REST API заметок."""

    def setUp(self) -> None:
        reset_notes()
        self.client = TestClient(notes_app)
        self.client.post("/notes", json={
            "title": "Первая", "content": "Текст про Flask",
            "tags": ["учёба"]})
        self.client.post("/notes", json={
            "title": "Вторая", "content": "Текст про FastAPI",
            "tags": ["учёба", "api"]})

    def test_list_and_filter(self) -> None:
        self.assertEqual(len(self.client.get("/notes").json()), 2)
        by_tag = self.client.get("/notes", params={"tag": "api"}).json()
        self.assertEqual(len(by_tag), 1)
        self.assertEqual(by_tag[0]["title"], "Вторая")
        by_query = self.client.get("/notes", params={"q": "flask"}).json()
        self.assertEqual(len(by_query), 1)
        self.assertEqual(by_query[0]["title"], "Первая")

    def test_pagination(self) -> None:
        page = self.client.get("/notes", params={"limit": 1,
                                                 "offset": 1}).json()
        self.assertEqual(len(page), 1)
        self.assertEqual(page[0]["title"], "Вторая")
        self.assertEqual(self.client.get("/notes", params={"limit": 0})
                         .status_code, 422)

    def test_create_has_timestamps(self) -> None:
        data = self.client.get("/notes/1").json()
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)

    def test_replace(self) -> None:
        response = self.client.put("/notes/1", json={
            "title": "Обновлённая", "content": "Новый текст"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["title"], "Обновлённая")
        self.assertEqual(data["tags"], [])
        self.assertGreaterEqual(data["updated_at"], data["created_at"])

    def test_delete_and_404(self) -> None:
        self.assertEqual(self.client.delete("/notes/1").status_code, 204)
        self.assertEqual(self.client.get("/notes/1").status_code, 404)
        self.assertEqual(self.client.delete("/notes/1").status_code, 404)

    def test_validation(self) -> None:
        response = self.client.post("/notes", json={"title": ""})
        self.assertEqual(response.status_code, 422)


class TestSqlAlchemy(unittest.TestCase):
    """Задание 9 (повышенная): подключение SQLAlchemy."""

    def setUp(self) -> None:
        self.engine = make_engine("sqlite:///:memory:")
        init_db(self.engine)

    def test_add_and_get(self) -> None:
        student = add_student(self.engine, "Иванов Иван", "220042-11", 5)
        self.assertEqual(student.id, 1)
        students = get_students(self.engine)
        self.assertEqual(len(students), 1)
        self.assertEqual(students[0].full_name, "Иванов Иван")

    def test_filter_by_group(self) -> None:
        add_student(self.engine, "А А", "220042-11", 4)
        add_student(self.engine, "Б Б", "221341", 5)
        filtered = get_students(self.engine, group="221341")
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].full_name, "Б Б")

    def test_update_grade(self) -> None:
        student = add_student(self.engine, "А А", "Г", 4)
        updated = update_grade(self.engine, student.id, 5)
        self.assertEqual(updated.grade, 5)
        with self.assertRaises(LookupError):
            update_grade(self.engine, 999, 5)

    def test_delete(self) -> None:
        student = add_student(self.engine, "А А", "Г", 4)
        delete_student(self.engine, student.id)
        self.assertEqual(get_students(self.engine), [])
        with self.assertRaises(LookupError):
            delete_student(self.engine, student.id)

    def test_validation(self) -> None:
        for args in [("", "Г", 5), ("А А", "", 5), ("А А", "Г", 6)]:
            with self.assertRaises(ValueError):
                add_student(self.engine, *args)


if __name__ == "__main__":
    unittest.main()

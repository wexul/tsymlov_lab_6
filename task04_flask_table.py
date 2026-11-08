"""Задание 4 (средняя сложность): страница с таблицей данных.

Flask-приложение: главная страница показывает таблицу студентов через
шаблон Jinja2 (templates/students.html), средний балл считается на
сервере. Дополнительно /api/students отдаёт те же данные в JSON.

Запуск:
    python task04_flask_table.py
    # открыть http://127.0.0.1:5004/
"""

from __future__ import annotations

from flask import Flask, jsonify, render_template

STUDENTS = [
    {"name": "Полошков Ярослав Витальевич", "group": "220042-11",
     "grade": 5},
    {"name": "Иванов Иван Иванович", "group": "220042-11", "grade": 4},
    {"name": "Петрова Анна Сергеевна", "group": "221341", "grade": 5},
    {"name": "Сидоров Сидор Сидорович", "group": "221141", "grade": 3},
]


def average_grade(students: list[dict]) -> float | None:
    """Средний балл списка студентов или None для пустого списка."""
    if not students:
        return None
    return sum(item["grade"] for item in students) / len(students)


def create_app() -> Flask:
    """Фабрика Flask-приложения (удобно для тестов)."""
    app = Flask(__name__)

    @app.route("/")
    def index() -> str:
        """HTML-страница с таблицей студентов."""
        return render_template("students.html", students=STUDENTS,
                               average=average_grade(STUDENTS))

    @app.route("/api/students")
    def students_json():
        """Те же данные в JSON."""
        return jsonify({"students": STUDENTS,
                        "average": average_grade(STUDENTS)})

    return app


app = create_app()

if __name__ == "__main__":
    app.run(port=5004, debug=False)

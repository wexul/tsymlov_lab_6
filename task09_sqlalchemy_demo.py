"""Задание 9 (повышенная сложность): подключение SQLAlchemy.

SQLAlchemy 2.0 (ORM, декларативный стиль): модель Student для SQLite,
функции CRUD (create/read/update/delete) с корректным управлением
сессиями. По умолчанию используется файл students.db; в тестах -
in-memory база через make_engine("sqlite:///:memory:").

Запуск:
    python task09_sqlalchemy_demo.py
"""

from __future__ import annotations

from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
)


class Base(DeclarativeBase):
    """Базовый класс декларативных моделей."""


class Student(Base):
    """Модель студента: таблица students."""

    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    group: Mapped[str] = mapped_column(String(20), nullable=False)
    grade: Mapped[int] = mapped_column(nullable=False)

    def __repr__(self) -> str:
        """Техническое представление записи."""
        return (f"Student(id={self.id}, {self.full_name!r}, "
                f"{self.group!r}, grade={self.grade})")


def make_engine(url: str = "sqlite:///students.db"):
    """Создаёт движок SQLAlchemy по URL базы."""
    return create_engine(url, echo=False)


def init_db(engine) -> None:
    """Создаёт таблицы по моделям."""
    Base.metadata.create_all(engine)


def add_student(engine, full_name: str, group: str,
                grade: int) -> Student:
    """Добавляет студента с валидацией и возвращает его с id."""
    if not full_name.strip():
        raise ValueError("ФИО не может быть пустым")
    if not group.strip():
        raise ValueError("группа не может быть пустой")
    if not 2 <= grade <= 5:
        raise ValueError("оценка должна быть от 2 до 5")
    with Session(engine) as session:
        student = Student(full_name=full_name.strip(),
                          group=group.strip(), grade=grade)
        session.add(student)
        session.commit()
        session.refresh(student)
        session.expunge(student)
        return student


def get_students(engine, group: str | None = None) -> list[Student]:
    """Возвращает студентов, опционально фильтруя по группе."""
    statement = select(Student)
    if group is not None:
        statement = statement.where(Student.group == group)
    with Session(engine) as session:
        return list(session.scalars(statement).all())


def update_grade(engine, student_id: int, grade: int) -> Student:
    """Обновляет оценку студента по id."""
    if not 2 <= grade <= 5:
        raise ValueError("оценка должна быть от 2 до 5")
    with Session(engine) as session:
        student = session.get(Student, student_id)
        if student is None:
            raise LookupError(f"студент с id={student_id} не найден")
        student.grade = grade
        session.commit()
        session.refresh(student)
        session.expunge(student)
        return student


def delete_student(engine, student_id: int) -> None:
    """Удаляет студента по id."""
    with Session(engine) as session:
        student = session.get(Student, student_id)
        if student is None:
            raise LookupError(f"студент с id={student_id} не найден")
        session.delete(student)
        session.commit()


def demo() -> None:
    """Демонстрация CRUD на in-memory базе SQLite."""
    engine = make_engine("sqlite:///:memory:")
    init_db(engine)
    print("SQLAlchemy: создана in-memory БД и таблица students")
    first = add_student(engine, "Полошков Ярослав Витальевич",
                        "220042-11", 5)
    add_student(engine, "Иванов Иван Иванович", "220042-11", 4)
    add_student(engine, "Петрова Анна Сергеевна", "221341", 5)
    print("INSERT: добавлено 3 записи")
    print("SELECT все:", *get_students(engine), sep="\n  ")
    print("SELECT по группе 220042-11:",
          len(get_students(engine, group="220042-11")), "записи")
    updated = update_grade(engine, first.id, 4)
    print(f"UPDATE: у студента id={first.id} теперь оценка "
          f"{updated.grade}")
    delete_student(engine, first.id)
    print(f"DELETE: удалён id={first.id}; осталось записей: "
          f"{len(get_students(engine))}")
    print("Попытка добавить оценку 10:")
    try:
        add_student(engine, "Тестов Тест", "1", 10)
    except ValueError as error:
        print(f"  Ошибка: {error}")


if __name__ == "__main__":
    demo()

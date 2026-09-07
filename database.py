import os

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SEED_TASKS = (
    ("Buy groceries", False),
    ("Sell groceries", False),
    ("Food", True),
)


def connect():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set")

    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def initialize_database():
    with connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT FALSE
            )
            """
        )
        task_count = connection.execute(
            "SELECT COUNT(*) AS task_count FROM tasks"
        ).fetchone()["task_count"]

        if task_count == 0:
            with connection.cursor() as cursor:
                cursor.executemany(
                    "INSERT INTO tasks (title, done) VALUES (%s, %s)",
                    SEED_TASKS,
                )


def to_task(row):
    if row is None:
        return None

    return {
        "id": row[0],
        "title": row[1],
        "done": bool(row[2]),
    }


def list_tasks():
    with connect() as connection:
        rows = connection.execute(
            "SELECT id, title, done FROM tasks ORDER BY id"
        ).fetchall()

    return [to_task(row) for row in rows]


def get_task(task_id):
    with connect() as connection:
        row = connection.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

    return to_task(row)


def insert_task(title):
    with connect() as connection:
        cursor = connection.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (title, 0),
        )
        row = connection.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()

    return to_task(row)


def update_task(task_id, title, done):
    with connect() as connection:
        connection.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
            (title, int(done), task_id),
        )
        row = connection.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

    return to_task(row)


def delete_task(task_id):
    with connect() as connection:
        cursor = connection.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,),
        )

    return cursor.rowcount > 0

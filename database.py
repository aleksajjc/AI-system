import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).with_name("tasks.db")
SEED_TASKS = (
    ("Buy groceries", 0),
    ("Sell groceries", 0),
    ("Food", 1),
)


def connect():
    return sqlite3.connect(DATABASE_PATH)


def initialize_database():
    with connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0 CHECK (done IN (0, 1))
            )
            """
        )
        task_count = connection.execute(
            "SELECT COUNT(*) FROM tasks"
        ).fetchone()[0]

        if task_count == 0:
            connection.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
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

# Task API
**Status:** 🚧 In Progress

A CRUD REST API for a to-do list, built with Python, FastAPI, and SQLite. The HTTP endpoints keep the same behavior as the original in-memory version, while every task is now stored on disk and survives server restarts.

## Install and run

Python 3.10 or newer is required.
```bash
python -m pip install fastapi uvicorn
```

Start the API with one command:

```bash
python -m uvicorn main:app --reload
```


## SQL exploration

One query run during Stage 4 was:

```sql
SELECT * FROM tasks;
```

It returned all three seeded tasks. Changes made directly with SQL were immediately visible through `GET /tasks` because both operations use the same `tasks.db` file.

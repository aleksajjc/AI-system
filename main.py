from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from database import get_task, initialize_database, list_tasks


app = FastAPI()

initialize_database()


tasks = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Sell groceries", "done": False},
    {"id": 3, "title": "Food", "done": True}
]


class TaskCreate(BaseModel):
    title: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": str(exc.detail)},
    )


@app.get("/", summary="Describe API endpoints")
def describe():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


@app.get("/health", summary="Check server health")
def check_health():
    return {"status": "ok"}


@app.get("/tasks", summary="List all tasks")
def getAll():
    return list_tasks()


@app.get("/tasks/{id}", summary="Get a single task by ID")
def getById(id: int):
    task = get_task(id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@app.post("/tasks", status_code=201, summary="Create a new task")
def create_task(task_data: TaskCreate):
    if not task_data.title or not task_data.title.strip():
        raise HTTPException(
            status_code=400,
            detail="Title is required and cannot be empty"
        )

    new_id = max([t["id"] for t in tasks], default=0) + 1

    new_task = {
        "id": new_id,
        "title": task_data.title.strip(),
        "done": False
    }

    tasks.append(new_task)

    return new_task


@app.put("/tasks/{id}", summary="Update an existing task")
def update_task(id: int, task_data: TaskUpdate):
    if task_data.title is None and task_data.done is None:
        raise HTTPException(
            status_code=400,
            detail="Empty body"
        )

    for task in tasks:
        if task["id"] == id:

            if task_data.title is not None:
                if not task_data.title.strip():
                    raise HTTPException(
                        status_code=400,
                        detail="Title cannot be empty"
                    )

                task["title"] = task_data.title.strip()

            if task_data.done is not None:
                task["done"] = task_data.done

            return task

    raise HTTPException(
        status_code=404,
        detail=f"Task {id} not found"
    )


@app.delete("/tasks/{id}", status_code=204, summary="Delete a task")
def delete_task(id: int):
    for index, task in enumerate(tasks):
        if task["id"] == id:
            del tasks[index]
            return

    raise HTTPException(
        status_code=404,
        detail=f"Task {id} not found"
    )

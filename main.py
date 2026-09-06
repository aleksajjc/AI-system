from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from database import (
    delete_task as delete_task_record,
    get_task,
    initialize_database,
    insert_task,
    list_tasks,
    update_task as update_task_record,
)


app = FastAPI()

initialize_database()


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


@app.exception_handler(RequestValidationError)
async def request_validation_handler(_: Request, __: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid request body"},
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

    return insert_task(task_data.title.strip())


@app.put("/tasks/{id}", summary="Update an existing task")
def update_task(id: int, task_data: TaskUpdate):
    if task_data.title is None and task_data.done is None:
        raise HTTPException(
            status_code=400,
            detail="Empty body"
        )

    task = get_task(id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    title = task["title"]
    if task_data.title is not None:
        title = task_data.title.strip()
        if not title:
            raise HTTPException(status_code=400, detail="Title cannot be empty")

    done = task["done"] if task_data.done is None else task_data.done
    return update_task_record(id, title, done)


@app.delete("/tasks/{id}", status_code=204, summary="Delete a task")
def delete_task(id: int):
    if not delete_task_record(id):
        raise HTTPException(status_code=404, detail="Task not found")

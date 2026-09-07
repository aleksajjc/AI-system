from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, SecretStr
from typing import Optional

from authentication import (
    AuthConfigurationError,
    AuthRejectedError,
    AuthUnavailableError,
    sign_in,
    sign_out,
    sign_up,
    verify_access_token,
)

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


class AuthCredentials(BaseModel):
    email: Optional[str] = None
    password: Optional[SecretStr] = None


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
        "endpoints": [
            "/tasks",
            "/auth/signup",
            "/auth/login",
            "/auth/logout",
            "/public/info",
            "/protected/profile",
            "/protected/dashboard",
        ],
    }


@app.get("/health", summary="Check server health")
def check_health():
    return {"status": "ok"}


def validated_credentials(credentials: AuthCredentials):
    email = credentials.email.strip() if credentials.email else ""
    password = credentials.password.get_secret_value() if credentials.password else ""
    if not email or not password.strip():
        raise HTTPException(status_code=400, detail="Email and password are required")
    return email, password


def authentication_unavailable():
    raise HTTPException(status_code=503, detail="Authentication service unavailable")


def require_user(authorization: Optional[str] = Header(default=None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Access token required")

    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1].strip():
        raise HTTPException(status_code=401, detail="Access token required")

    token = parts[1].strip()
    try:
        user = verify_access_token(token)
    except AuthRejectedError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    except (AuthConfigurationError, AuthUnavailableError):
        authentication_unavailable()

    return {"token": token, "user": user}


@app.post("/auth/signup", status_code=201, summary="Create a user account")
def signup(credentials: AuthCredentials):
    email, password = validated_credentials(credentials)
    try:
        user = sign_up(email, password)
    except AuthRejectedError:
        raise HTTPException(status_code=400, detail="Unable to create account")
    except (AuthConfigurationError, AuthUnavailableError):
        authentication_unavailable()
    return {"user": user}


@app.post("/auth/login", summary="Log in and receive tokens")
def login(credentials: AuthCredentials):
    email, password = validated_credentials(credentials)
    try:
        return sign_in(email, password)
    except AuthRejectedError:
        raise HTTPException(status_code=401, detail="Invalid login credentials")
    except (AuthConfigurationError, AuthUnavailableError):
        authentication_unavailable()


@app.post("/auth/logout", status_code=204, summary="Log out")
def logout(authenticated=Depends(require_user)):
    try:
        sign_out(authenticated["token"])
    except AuthRejectedError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    except (AuthConfigurationError, AuthUnavailableError):
        authentication_unavailable()


@app.get("/public/info", summary="Read public information")
def public_info():
    return {"message": "Welcome stranger! This info is public."}


@app.get("/protected/profile", summary="Read the authenticated profile")
def protected_profile(authenticated=Depends(require_user)):
    return authenticated["user"]


@app.get("/protected/dashboard", summary="Read the protected dashboard")
def protected_dashboard(authenticated=Depends(require_user)):
    return {
        "message": "Welcome to the protected dashboard",
        "user_id": authenticated["user"]["id"],
    }


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

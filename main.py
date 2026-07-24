from fastapi import FastAPI, HTTPException, Request

app = FastAPI()


tasks = [{"id": 1, "title": "Buy groceries", "done": False},
         {"id": 2, "title": "Sell groceries", "done": False},
         {"id": 3, "title": "Food", "done": True}]


@app.get("/")
def describe():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get('/health')
def check_health():
    return {"status": "ok"}


@app.get('/tasks')
def getAll():
    return tasks

@app.get('/tasks/{id}')
def getById(id: int):
    for task in tasks:
        if task["id"] == id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {id} not found")

@app.post("/tasks", status_code=201)
async def create_task(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    title = body.get("title")
    if not title or not str(title).strip():
        raise HTTPException(
            status_code=400, detail="Title is required and cannot be empty"
        )

    # Calculate next ID
    new_id = max([t["id"] for t in tasks], default=0) + 1

    # Create new task object
    new_task = {"id": new_id, "title": str(title).strip(), "done": False}

    tasks.append(new_task)
    return new_task

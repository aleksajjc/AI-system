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

    new_id = max([t["id"] for t in tasks], default=0) + 1
    new_task = {"id": new_id, "title": str(title).strip(), "done": False}
    tasks.append(new_task)
    return new_task

@app.put("/tasks/{id}")
async def update_task(id: int, request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")
        
    if not body:
        raise HTTPException(status_code=400, detail="Empty body")
        
    for task in tasks:
        if task["id"] == id:
            if "title" in body:
                if not body["title"] or not str(body["title"]).strip():
                    raise HTTPException(status_code=400, detail="Title cannot be empty")
                task["title"] = str(body["title"]).strip()
            if "done" in body:
                if not isinstance(body["done"], bool):
                    raise HTTPException(status_code=400, detail="Done must be a boolean")
                task["done"] = body["done"]
            return task
            
    raise HTTPException(status_code=404, detail=f"Task {id} not found")

@app.delete("/tasks/{id}", status_code=204)
def delete_task(id: int):
    for index, task in enumerate(tasks):
        if task["id"] == id:
            del tasks[index]
            return
    raise HTTPException(status_code=404, detail=f"Task {id} not found")

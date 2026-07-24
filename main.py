import uvicorn
from fastapi import FastAPI, HTTPException

app = FastAPI()


tasks = [{"id":1,"title":"Buy groceries","done":False},
         {"id":2,"title":"Sell groceries","done":False},
         {"id":3,"title":"Food","done":True}]


@app.get("/")
def describe():
    return{"name":"FastAPI","version":"1.0", "endpoints":["/tasks"]}

@app.get('/health')
def check_health():
    return{"status":"ok"}


@app.get('/tasks')
def getAll():
    return{"tasks":tasks}

@app.get('/tasks/{id}')
def getById(id: int):
    for task in tasks:
        if task["id"] == id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {id} not found")


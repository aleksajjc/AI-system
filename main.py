import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def describe():
    return{"name":"FastAPI","version":"1.0", "endpoints":["/tasks"]}

@app.get('/health')
def check_health():
    return{"status":"ok"}
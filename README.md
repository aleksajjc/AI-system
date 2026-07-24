# Task API 
**Status:** 🚧 In Progress

A simple CRUD REST API that manages a to-do list. Built with Python and FastAPI, this API allows you to create, read, update, and delete tasks. All data is stored in memory.
## How to install & run it
You can install all dependencies and start the server with this single command (run it inside your project directory):
```bash
pip install fastapi uvicorn && uvicorn main:app --reload
```
### Example Response

```http
HTTP/1.1 200 OK
date: Fri, 24 Jul 2026 12:52:24 GMT
server: uvicorn
content-length: 45
content-type: application/json

{
  "id": 1,
  "title": "Buy groceries",
  "done": false
}
```
<img width="1455" height="569" alt="fastAPI" src="https://github.com/user-attachments/assets/2b68c586-190b-4e93-9010-b9efd9ac4cc3" />

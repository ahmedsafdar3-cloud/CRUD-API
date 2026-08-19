from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(title="Task API")


class TaskIn(BaseModel):
    title: str = ""
    done: bool = False

# In-memory "database" — resets every time the server restarts
tasks = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Walk the dog", "done": False},
    {"id": 3, "title": "Finish assignment", "done": True},
]


@app.get("/")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"],
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/tasks")
def get_tasks():
    return tasks


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"},
    )


@app.post("/tasks", status_code=201)
def create_task(task: TaskIn):
    title = task.title.strip()
    if not title:
        return JSONResponse(
            status_code=400,
            content={"error": "title is required and cannot be empty"},
        )

    next_id = max((t["id"] for t in tasks), default=0) + 1
    new_task = {"id": next_id, "title": title, "done": False}
    tasks.append(new_task)
    return JSONResponse(status_code=201, content=new_task)


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskIn):
    title = task.title.strip()
    if not title:
        return JSONResponse(
            status_code=400,
            content={"error": "title is required and cannot be empty"},
        )

    for existing in tasks:
        if existing["id"] == task_id:
            existing["title"] = title
            existing["done"] = task.done
            return existing

    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"},
    )


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    for existing in tasks:
        if existing["id"] == task_id:
            tasks.remove(existing)
            return JSONResponse(status_code=204, content=None)

    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"},
    )

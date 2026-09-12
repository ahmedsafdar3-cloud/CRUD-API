from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from repository import (
    get_all_tasks,
    get_task,
    create_task,
    update_task,
    delete_task,
)


# -------------------------
# FASTAPI
# -------------------------

app = FastAPI(title="Task API")


class TaskIn(BaseModel):
    title: str = ""
    done: bool = False


# -------------------------
# ROOT
# -------------------------

@app.get("/")
def read_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"],
    }


# -------------------------
# HEALTH
# -------------------------

@app.get("/health")
def health_check():
    return {"status": "ok"}


# -------------------------
# GET ALL TASKS
# -------------------------

@app.get("/tasks")
def get_tasks():
    return get_all_tasks()


# -------------------------
# GET ONE TASK
# -------------------------

@app.get("/tasks/{task_id}")
def get_one_task(task_id: int):

    task = get_task(task_id)

    if task is None:
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"}
        )

    return task


# -------------------------
# CREATE TASK
# -------------------------

@app.post("/tasks", status_code=201)
def create_new_task(task: TaskIn):

    title = task.title.strip()

    if not title:
        return JSONResponse(
            status_code=400,
            content={"error": "title is required and cannot be empty"},
        )

    new_task = create_task(title, False)

    return JSONResponse(
        status_code=201,
        content=new_task
    )


# -------------------------
# UPDATE TASK
# -------------------------

@app.put("/tasks/{task_id}")
def update_existing_task(task_id: int, task: TaskIn):

    title = task.title.strip()

    if not title:
        return JSONResponse(
            status_code=400,
            content={"error": "title is required and cannot be empty"},
        )

    updated_task = update_task(
        task_id,
        title,
        task.done
    )

    if updated_task is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} not found"},
        )

    return updated_task


# -------------------------
# DELETE TASK
# -------------------------

@app.delete("/tasks/{task_id}", status_code=204)
def delete_existing_task(task_id: int):

    deleted = delete_task(task_id)

    if not deleted:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} not found"},
        )

    return Response(status_code=204)
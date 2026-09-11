from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sqlite3


# -------------------------
# DATABASE SETUP
# -------------------------

connection = sqlite3.connect("tasks.db", check_same_thread=False)
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    title TEXT,
    done INTEGER
)
""")

cursor.execute("SELECT COUNT(*) FROM tasks")
count = cursor.fetchone()[0]

if count == 0:
    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        ("Buy milk", 0)
    )

    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        ("Walk the dog", 0)
    )

    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        ("Finish assignment", 1)
    )

connection.commit()


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
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()

    tasks = []

    for row in rows:
        task = {
            "id": row[0],
            "title": row[1],
            "done": bool(row[2])
        }

        tasks.append(task)

    return tasks


# -------------------------
# GET ONE TASK
# -------------------------

@app.get("/tasks/{task_id}")
def get_task(task_id: int):

    cursor.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    )

    row = cursor.fetchone()

    if row is None:
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"}
        )

    task = {
        "id": row[0],
        "title": row[1],
        "done": bool(row[2])
    }

    return task


# -------------------------
# CREATE TASK
# -------------------------

@app.post("/tasks", status_code=201)
def create_task(task: TaskIn):

    title = task.title.strip()

    if not title:
        return JSONResponse(
            status_code=400,
            content={"error": "title is required and cannot be empty"},
        )

    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (title, 0)
    )

    connection.commit()

    new_id = cursor.lastrowid

    new_task = {
        "id": new_id,
        "title": title,
        "done": False
    }

    return JSONResponse(
        status_code=201,
        content=new_task
    )


# -------------------------
# UPDATE TASK
# -------------------------

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskIn):

    title = task.title.strip()

    if not title:
        return JSONResponse(
            status_code=400,
            content={"error": "title is required and cannot be empty"},
        )

    cursor.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    )

    row = cursor.fetchone()

    if row is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} not found"},
        )

    cursor.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (title, int(task.done), task_id)
    )

    connection.commit()

    updated_task = {
        "id": task_id,
        "title": title,
        "done": task.done
    }

    return updated_task


# -------------------------
# DELETE TASK
# -------------------------

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):

    cursor.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    )

    row = cursor.fetchone()

    if row is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Task {task_id} not found"},
        )

    cursor.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    connection.commit()

    return Response(status_code=204)
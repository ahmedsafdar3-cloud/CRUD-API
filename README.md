# Task API

A small in-memory CRUD API for managing a to-do list, built with FastAPI.

## Setup

```bash
python -m venv env
env\Scripts\activate        # Windows (cmd)
# .\env\Scripts\Activate.ps1  # Windows (PowerShell)
# source env/Scripts/activate # Git Bash / macOS / Linux

pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload
```

- API base: http://localhost:8000
- Interactive docs (Swagger UI): http://localhost:8000/docs

## Endpoints

| Method | Path         | Description              |
|--------|--------------|---------------------------|
| GET    | /            | API info                  |
| GET    | /health      | Health check               |
| GET    | /tasks       | List all tasks             |
| GET    | /tasks/{id}  | Get one task                |
| POST   | /tasks       | Create a task               |
| PUT    | /tasks/{id}  | Update a task                |
| DELETE | /tasks/{id}  | Delete a task                 |

## Try it with curl

```bash
curl -i http://localhost:8000/tasks

curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Buy milk\"}"

curl -i -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Buy oat milk\",\"done\":true}"

curl -i -X DELETE http://localhost:8000/tasks/1
```

## Notes

- Data lives in memory only — it resets whenever the server restarts.
- 404 is returned for unknown task ids; 400 is returned when `title` is missing or empty.

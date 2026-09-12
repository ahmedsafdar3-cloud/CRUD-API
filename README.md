# Task API

A simple CRUD Task API built with FastAPI and PostgreSQL, containerized using Docker Compose.

## Tech Stack

* Python 3.12
* FastAPI
* PostgreSQL 16
* psycopg
* Docker
* Docker Compose

## Project Structure

```text
CRUD-Python/
├── main.py
├── repository.py
├── Dockerfile
├── docker-compose.yml
├── init.sql
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Setup

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd CRUD-Python
```

### 2. Create the environment file

Copy `.env.example` to `.env` and configure:

```text
DATABASE_URL=postgres://postgres:dev@localhost:5432/tasks
```

The `.env` file is ignored by Git and should not be committed.

### 3. Start the application

```bash
docker compose up --build
```

The API will be available at:

```text
http://localhost:8000
```

## API Endpoints

| Method | Endpoint      | Description     |
| ------ | ------------- | --------------- |
| GET    | `/`           | API information |
| GET    | `/health`     | Health check    |
| GET    | `/tasks`      | Get all tasks   |
| GET    | `/tasks/{id}` | Get a task      |
| POST   | `/tasks`      | Create a task   |
| PUT    | `/tasks/{id}` | Update a task   |
| DELETE | `/tasks/{id}` | Delete a task   |

## Example

Get all tasks:

```bash
curl -i http://localhost:8000/tasks
```

Example response:

```json
[
  {"id":1,"title":"Buy milk","done":false},
  {"id":2,"title":"Walk the dog","done":false},
  {"id":3,"title":"Finish assignment","done":true}
]
```

## Database Persistence

PostgreSQL runs in a Docker container using the `taskdata` named volume.

The database data survives:

```bash
docker compose down
docker compose up
```

The database volume is only removed when using:

```bash
docker compose down -v
```

## Database Initialization

`init.sql` creates the `tasks` table and inserts the initial seed data when the PostgreSQL database is first initialized.

## Clean Clone

A fresh clone only requires:

```bash
git clone <your-repository-url>
cd CRUD-Python
```

Create the `.env` file from `.env.example`, then run:

```bash
docker compose up --build
```

No local PostgreSQL installation is required.

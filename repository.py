import os
import psycopg
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

@lru_cache(maxsize=1)
def get_connection():
    return psycopg.connect(DATABASE_URL)

def hello_repository():
    return "Repository connected to PostgreSQL!"

def create_table():
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title TEXT,
                done BOOLEAN
            )
        """)

    connection.commit()

def seed_tasks():
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM tasks")
        count = cursor.fetchone()[0]

        if count == 0:
            cursor.execute(
                "INSERT INTO tasks (title, done) VALUES (%s, %s)",
                ("Buy milk", False)
            )

            cursor.execute(
                "INSERT INTO tasks (title, done) VALUES (%s, %s)",
                ("Walk the dog", False)
            )

            cursor.execute(
                "INSERT INTO tasks (title, done) VALUES (%s, %s)",
                ("Review project documentation", True)
            )

    connection.commit()

def get_all_tasks():
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM tasks")
        rows = cursor.fetchall()

    tasks = []

    for row in rows:
        task = {
            "id": row[0],
            "title": row[1],
            "done": row[2]
        }

        tasks.append(task)

    return tasks

def get_task(task_id):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM tasks WHERE id = %s",
            (task_id,)
        )

        row = cursor.fetchone()

    if row is None:
        return None

    return {
        "id": row[0],
        "title": row[1],
        "done": row[2]
    }

def create_task(title, done=False):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id",
            (title, done)
        )

        new_id = cursor.fetchone()[0]

    connection.commit()

    return {
        "id": new_id,
        "title": title,
        "done": done
    }

def update_task(task_id, title, done):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE tasks
            SET title = %s, done = %s
            WHERE id = %s
            RETURNING id, title, done
            """,
            (title, done, task_id)
        )

        row = cursor.fetchone()

    if row is None:
        connection.rollback()
        return None

    connection.commit()

    return {
        "id": row[0],
        "title": row[1],
        "done": row[2]
    }

def delete_task(task_id):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM tasks WHERE id = %s RETURNING id",
            (task_id,)
        )

        row = cursor.fetchone()

    if row is None:
        connection.rollback()
        return False

    connection.commit()

    return True

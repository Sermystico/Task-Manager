import psycopg
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg.connect(
    host=os.getenv("DB_HOST"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

def get_all_tasks():
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, description, completed FROM tasks")

    tasks = cursor.fetchall()

    cursor.close()

    return tasks

def create_task(title, description, completed):
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO tasks (title, description, completed)
        VALUES (%s, %s, %s)
        RETURNING id, title, description, completed
        """,
        (title, description, completed)
    )

    task = cursor.fetchone()

    conn.commit()
    cursor.close()

    return task

def get_task(task_id):
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, title, description, completed
        FROM tasks
        WHERE id = %s
        """,
        (task_id,)
    )

    task = cursor.fetchone()

    cursor.close()

    return task

def update_task(task_id, title, description, completed):
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE tasks
        SET title = %s, description = %s, completed = %s
        WHERE id = %s
        RETURNING id, title, description, completed
        """,
        (title, description, completed, task_id)
    )

    task = cursor.fetchone()

    conn.commit()
    cursor.close()

    return task

def delete_task(task_id):
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM tasks
        WHERE id = %s
        RETURNING id
        """,
        (task_id,)
    )

    task = cursor.fetchone()

    conn.commit()
    cursor.close()

    return task
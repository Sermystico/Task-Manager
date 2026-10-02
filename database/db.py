import psycopg
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg.connect(
    host=os.getenv("DB_HOST"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    autocommit=True
)

def get_all_tasks(user_id):
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, title, description, completed, user_id
        FROM tasks
        WHERE user_id = %s
        """,
        (user_id,)
    )
    tasks = cursor.fetchall()
    cursor.close()
    return tasks

def create_task(title, description, completed, user_id):
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO tasks (title, description, completed, user_id)
        VALUES (%s, %s, %s, %s)
        RETURNING id, title, description, completed, user_id
        """,
        (title, description, completed, user_id)
    )
    task = cursor.fetchone()
    conn.commit()
    cursor.close()
    return task

def get_task(task_id, user_id):
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, title, description, completed, user_id
        FROM tasks
        WHERE id = %s AND user_id = %s
        """,
        (task_id, user_id)
    )
    task = cursor.fetchone()
    cursor.close()
    return task

def update_task(task_id, title, description, completed, user_id):
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE tasks
        SET title = %s, description = %s, completed = %s
        WHERE id = %s AND user_id = %s
        RETURNING id, title, description, completed, user_id
        """,
        (title, description, completed, task_id, user_id)
    )
    task = cursor.fetchone()
    conn.commit()
    cursor.close()
    return task

def delete_task(task_id, user_id):
    cursor = conn.cursor()
    cursor.execute(
        """
        DELETE FROM tasks
        WHERE id = %s AND user_id = %s
        RETURNING id
        """,
        (task_id, user_id)
    )
    task = cursor.fetchone()
    conn.commit()
    cursor.close()
    return task

def create_user(username, password_hash):
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO users (username, password_hash)
        VALUES (%s, %s)
        RETURNING id, username
        """,
        (username, password_hash)
    )
    user = cursor.fetchone()
    conn.commit()
    cursor.close()
    return user

def get_user_by_username(username):
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, username, password_hash
        FROM users
        WHERE username = %s
        """,
        (username,)
    )
    user = cursor.fetchone()
    cursor.close()
    return user


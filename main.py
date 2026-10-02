from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field

from auth.models import User
from auth.security import hash_password, verify_password
from auth.jwt import create_access_token
from auth.dependencies import get_current_user
from fastapi.security import OAuth2PasswordRequestForm

from database.db import (
    get_all_tasks, create_task, get_task, update_task, 
    delete_task, create_user, get_user_by_username
)

app = FastAPI()

class Task(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    completed: bool = False

@app.get("/")
def home():
    return {"message": "Task Management API is running"}

@app.get("/tasks")
def get_tasks(current_user=Depends(get_current_user)):
    return get_all_tasks(current_user["user_id"])

@app.post("/register")
def register_user(user: User):
    password_hash = hash_password(user.password)

    return create_user(
        user.username,
        password_hash
    )

@app.post("/login")
def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    existing_user = get_user_by_username(form_data.username)

    if existing_user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    password_hash = existing_user[2]

    if not verify_password(form_data.password, password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    access_token = create_access_token(
        existing_user[0],
        existing_user[1]
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.post("/tasks")
def create_new_task(
    task: Task,
    current_user=Depends(get_current_user)
):
    return create_task(
        task.title,
        task.description,
        task.completed,
        current_user["user_id"]
    )

@app.get("/tasks/{task_id}")
def get_one_task(
    task_id: int,
    current_user=Depends(get_current_user)
):
    task = get_task(
        task_id,
        current_user["user_id"]
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task

@app.put("/tasks/{task_id}")
def update_one_task(
    task_id: int,
    task: Task,
    current_user=Depends(get_current_user)
):
    updated_task = update_task(
        task_id,
        task.title,
        task.description,
        task.completed,
        current_user["user_id"]
    )

    if updated_task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return updated_task

@app.delete("/tasks/{task_id}")
def delete_one_task(
    task_id: int,
    current_user=Depends(get_current_user)
):
    deleted_task = delete_task(
        task_id,
        current_user["user_id"]
    )

    if deleted_task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return {"message": "Task deleted"}

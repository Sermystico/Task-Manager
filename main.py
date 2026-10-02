from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from database.db import (
    get_all_tasks,
    create_task,
    get_task,
    update_task,
    delete_task
)
app = FastAPI()

@app.get("/")
def home():
    return {"message": "Task Management API is running"}

class Task(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    completed: bool = False

@app.post("/tasks")
def create_new_task(task: Task):
    return create_task(
        task.title,
        task.description,
        task.completed
    )

@app.get("/tasks")
def get_tasks():
    return get_all_tasks()

@app.get("/tasks/{task_id}")
def get_one_task(task_id: int):
    task = get_task(task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task

@app.delete("/tasks/{task_id}")
def delete_one_task(task_id: int):
    deleted_task = delete_task(task_id)

    if deleted_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return {"message": "Task deleted"}

@app.put("/tasks/{task_id}")
def update_one_task(task_id: int, task: Task):
    updated_task = update_task(
        task_id,
        task.title,
        task.description,
        task.completed
    )

    if updated_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return updated_task

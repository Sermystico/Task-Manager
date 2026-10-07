import psycopg
from typing import List
from fastapi import APIRouter, Depends, HTTPException

from core.database import get_db_connection
from auth.dependencies import get_current_user
from models.task import TaskCreate, TaskUpdate, TaskResponse
from repositories.task_repository import TaskRepository
from services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])

# Dependency Providers
def get_task_repository(conn: psycopg.Connection = Depends(get_db_connection)) -> TaskRepository:
    return TaskRepository(conn)

def get_task_service(repo: TaskRepository = Depends(get_task_repository)) -> TaskService:
    return TaskService(repo)

# Routes
@router.get("", response_model=List[TaskResponse])
def get_tasks(
    current_user: dict = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """Retrieve all tasks for the authenticated user."""
    return service.get_tasks_for_user(current_user["user_id"])

@router.post("", response_model=TaskResponse)
def create_new_task(
    task: TaskCreate,
    current_user: dict = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """Create a new task."""
    return service.create_task(task, current_user["user_id"])

@router.get("/{task_id}", response_model=TaskResponse)
def get_one_task(
    task_id: int,
    current_user: dict = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """Retrieve a specific task by ID."""
    task = service.get_task(task_id, current_user["user_id"])
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskResponse)
def update_one_task(
    task_id: int,
    task: TaskUpdate,
    current_user: dict = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """Update a specific task."""
    updated_task = service.update_task(task_id, task, current_user["user_id"])
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task

@router.delete("/{task_id}")
def delete_one_task(
    task_id: int,
    current_user: dict = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    """Delete a task."""
    success = service.delete_task(task_id, current_user["user_id"])
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted"}

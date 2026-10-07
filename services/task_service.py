from typing import List, Optional
from repositories.task_repository import TaskRepository
from models.task import TaskCreate, TaskUpdate, TaskResponse

class TaskService:
    def __init__(self, repository: TaskRepository):
        self.repo = repository

    def get_tasks_for_user(self, user_id: int) -> List[TaskResponse]:
        """Business rule: Users can only retrieve their own tasks."""
        return self.repo.get_all_by_user(user_id)

    def create_task(self, task: TaskCreate, user_id: int) -> TaskResponse:
        """Business rule: Task is associated with the creating user."""
        return self.repo.create(task.title, task.description, task.completed, user_id)

    def get_task(self, task_id: int, user_id: int) -> Optional[TaskResponse]:
        """Business rule: Users can only retrieve tasks they own."""
        task = self.repo.get_by_id(task_id)
        if not task or task.user_id != user_id:
            return None
        return task

    def update_task(self, task_id: int, task_update: TaskUpdate, user_id: int) -> Optional[TaskResponse]:
        """Business rule: Users can only update tasks they own."""
        existing_task = self.get_task(task_id, user_id)
        if not existing_task:
            return None
        
        return self.repo.update(
            task_id, 
            task_update.title, 
            task_update.description, 
            task_update.completed
        )

    def delete_task(self, task_id: int, user_id: int) -> bool:
        """Business rule: Users can only delete tasks they own."""
        existing_task = self.get_task(task_id, user_id)
        if not existing_task:
            return False
            
        return self.repo.delete(task_id)

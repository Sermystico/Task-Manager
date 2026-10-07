import psycopg
from typing import List, Optional
from models.task import TaskResponse

class TaskRepository:
    def __init__(self, conn: psycopg.Connection):
        self.conn = conn

    def _map_to_model(self, row: tuple) -> TaskResponse:
        return TaskResponse(
            id=row[0],
            title=row[1],
            description=row[2],
            completed=row[3],
            user_id=row[4]
        )

    def get_all_by_user(self, user_id: int) -> List[TaskResponse]:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, title, description, completed, user_id
                FROM tasks
                WHERE user_id = %s
                ORDER BY id DESC
                """,
                (user_id,)
            )
            rows = cursor.fetchall()
            return [self._map_to_model(row) for row in rows]

    def create(self, title: str, description: str, completed: bool, user_id: int) -> TaskResponse:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO tasks (title, description, completed, user_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id, title, description, completed, user_id
                """,
                (title, description, completed, user_id)
            )
            row = cursor.fetchone()
            self.conn.commit()
            return self._map_to_model(row)

    def get_by_id(self, task_id: int) -> Optional[TaskResponse]:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, title, description, completed, user_id
                FROM tasks
                WHERE id = %s
                """,
                (task_id,)
            )
            row = cursor.fetchone()
            return self._map_to_model(row) if row else None

    def update(self, task_id: int, title: str, description: str, completed: bool) -> Optional[TaskResponse]:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE tasks
                SET title = %s, description = %s, completed = %s
                WHERE id = %s
                RETURNING id, title, description, completed, user_id
                """,
                (title, description, completed, task_id)
            )
            row = cursor.fetchone()
            self.conn.commit()
            return self._map_to_model(row) if row else None

    def delete(self, task_id: int) -> bool:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM tasks
                WHERE id = %s
                RETURNING id
                """,
                (task_id,)
            )
            row = cursor.fetchone()
            self.conn.commit()
            return row is not None

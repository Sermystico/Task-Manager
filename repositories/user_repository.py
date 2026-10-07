import psycopg
from typing import Optional, Tuple
from models.user import UserResponse

class UserRepository:
    def __init__(self, conn: psycopg.Connection):
        self.conn = conn

    def create(self, username: str, password_hash: str) -> UserResponse:
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (username, password_hash)
                VALUES (%s, %s)
                RETURNING id, username
                """,
                (username, password_hash)
            )
            row = cursor.fetchone()
            self.conn.commit()
            return UserResponse(id=row[0], username=row[1])

    def get_by_username_with_password(self, username: str) -> Optional[Tuple[UserResponse, str]]:
        """Returns the user response model and the password hash."""
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, username, password_hash
                FROM users
                WHERE username = %s
                """,
                (username,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            user = UserResponse(id=row[0], username=row[1])
            return user, row[2]

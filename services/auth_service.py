import psycopg
from typing import Tuple
from models.user import UserCreate, UserResponse
from repositories.user_repository import UserRepository
from auth.security import hash_password, verify_password
from auth.jwt import create_access_token

class AuthException(Exception):
    pass

class UsernameTakenException(Exception):
    pass

class AuthService:
    def __init__(self, repository: UserRepository):
        self.repo = repository

    def register_user(self, user: UserCreate) -> UserResponse:
        """Business rule: username must be unique."""
        password_hash = hash_password(user.password)
        try:
            return self.repo.create(user.username, password_hash)
        except psycopg.errors.UniqueViolation:
            raise UsernameTakenException("Username already registered")

    def authenticate_user(self, username: str, password: str) -> dict:
        """Business rule: verify credentials, issue token."""
        result = self.repo.get_by_username_with_password(username)
        if not result:
            raise AuthException("Invalid username or password")
        
        user, password_hash = result
        if not verify_password(password, password_hash):
            raise AuthException("Invalid username or password")
            
        access_token = create_access_token(user.id, user.username)
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

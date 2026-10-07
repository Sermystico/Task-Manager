import psycopg
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from core.database import get_db_connection
from models.user import UserCreate, UserResponse
from repositories.user_repository import UserRepository
from services.auth_service import AuthService, AuthException, UsernameTakenException

router = APIRouter(tags=["Auth"])

# Dependency Providers
def get_user_repository(conn: psycopg.Connection = Depends(get_db_connection)) -> UserRepository:
    return UserRepository(conn)

def get_auth_service(repo: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(repo)

# Routes
@router.post("/register", response_model=UserResponse)
def register_user(
    user: UserCreate,
    service: AuthService = Depends(get_auth_service)
):
    try:
        return service.register_user(user)
    except UsernameTakenException as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service)
):
    try:
        return service.authenticate_user(form_data.username, form_data.password)
    except AuthException as e:
        raise HTTPException(status_code=401, detail=str(e))

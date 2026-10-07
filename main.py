from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from auth.models import User
from auth.security import hash_password, verify_password
from auth.jwt import create_access_token
from auth.dependencies import get_current_user
from fastapi.security import OAuth2PasswordRequestForm

from database.db import (
    create_user, get_user_by_username
)
from handlers import task_handler

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(task_handler.router)

@app.get("/")
def home():
    return {"message": "Task Management API is running"}

import psycopg

@app.post("/register")
def register_user(user: User):
    password_hash = hash_password(user.password)

    try:
        return create_user(
            user.username,
            password_hash
        )
    except psycopg.errors.UniqueViolation:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
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



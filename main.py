from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from handlers import task_handler, auth_handler

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_handler.router)
app.include_router(task_handler.router)

@app.get("/")
def home():
    return {"message": "Task Management API is running"}

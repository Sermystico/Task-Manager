# Task Management API

A lightweight, robust RESTful API built with **FastAPI** and **PostgreSQL** (using `psycopg`) for managing tasks.

---

## Features

- **Authentication**: JWT-based user registration and login (`bcrypt` hashing).
- **User-Specific Tasks**: Secure CRUD operations ensuring tasks are strictly isolated per user.
- **Data Validation**: Request validation powered by Pydantic.
- **Relational Storage**: Direct, efficient PostgreSQL queries via `psycopg`.
- **Auto-Generated Documentation**: Interactive API documentation via Swagger UI and ReDoc.

---

## Architecture

This project uses a **Layered Monolith Architecture** to cleanly separate concerns:

- **Handlers (`handlers/`)**: Defines the API endpoints (FastAPI routers). Responsible for HTTP request parsing, response formatting, and dependency injection.
- **Services (`services/`)**: Contains business logic and domain rules. Enforces constraints (e.g. user isolation).
- **Repositories (`repositories/`)**: Encapsulates all raw SQL queries (`psycopg`) and database interaction. Maps rows to Pydantic models.
- **Models (`models/`)**: Pydantic schemas for data validation and serialization.
- **Core (`core/`)**: Application configuration and database connection providers.

**Request Flow:** `HTTP Request` &rarr; `Handler` &rarr; `Service` &rarr; `Repository` &rarr; `PostgreSQL`

---

## Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Server**: [Uvicorn](https://www.uvicorn.org/)
- **Database Driver**: [psycopg (v3)](https://www.psycopg.org/psycopg3/)
- **Data Validation**: [Pydantic](https://docs.pydantic.dev/)
- **Environment Management**: [python-dotenv](https://github.com/theskumar/python-dotenv)

---

## Getting Started

### 1. Prerequisites

- Python 3.10+
- PostgreSQL server installed and running

### 2. Clone the Repository

```bash
git clone https://github.com/Sermystico/backend_practise.git
cd backend_practise
```

### 3. Set Up Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install fastapi uvicorn "psycopg[binary]" python-dotenv pydantic
```

*(Optional: generate `requirements.txt` via `pip freeze > requirements.txt`)*

### 5. Database Setup

Create a PostgreSQL database (e.g. `task_management`) and set up the `tasks` table:

```sql
CREATE DATABASE task_management;

\c task_management;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
);
```

### 6. Environment Configuration

Copy `.env.example` to create your local `.env`:

```bash
cp .env.example .env
```

Edit `.env` with your PostgreSQL credentials:

```env
DB_HOST=localhost
DB_NAME=task_management
DB_USER=postgres
DB_PASSWORD=your_password_here
JWT_SECRET=your_secret_here
JWT_ALGORITHM=HS256
```

---

## Running the Application

Start the development server with hot-reload enabled:

```bash
uvicorn main:app --reload
```

The server will be accessible at `http://127.0.0.1:8000`.

---

## API Contract

The frontend strictly depends on this API contract. The backend implementation (Handlers, Services, Repositories) can change, but this request/response format remains constant.

### Authentication

**`POST /register`**
- **Auth:** None
- **Body:** JSON `{"username": "...", "password": "..."}`
- **Success (200):** `{"id": 1, "username": "..."}`
- **Error (400):** `{"detail": "Username already registered"}`

**`POST /login`**
- **Auth:** None
- **Body:** Form Data `username=...&password=...`
- **Success (200):** `{"access_token": "...", "token_type": "bearer"}`
- **Error (401):** `{"detail": "Invalid username or password"}`

### Tasks

**`GET /tasks`**
- **Auth:** Bearer JWT
- **Success (200):** Array of objects `[{"id": 1, "title": "...", "description": "...", "completed": false, "user_id": 1}]`

**`POST /tasks`**
- **Auth:** Bearer JWT
- **Body:** JSON `{"title": "...", "description": "...", "completed": false}`
- **Success (200):** `{"id": 1, "title": "...", "description": "...", "completed": false, "user_id": 1}`

**`GET /tasks/{task_id}`**
- **Auth:** Bearer JWT
- **Success (200):** `{"id": 1, "title": "...", "description": "...", "completed": false, "user_id": 1}`
- **Error (404):** `{"detail": "Task not found"}`

**`PUT /tasks/{task_id}`**
- **Auth:** Bearer JWT
- **Body:** JSON `{"title": "...", "description": "...", "completed": true}`
- **Success (200):** `{"id": 1, "title": "...", "description": "...", "completed": true, "user_id": 1}`
- **Error (404):** `{"detail": "Task not found"}`

**`DELETE /tasks/{task_id}`**
- **Auth:** Bearer JWT
- **Success (200):** `{"message": "Task deleted"}`
- **Error (404):** `{"detail": "Task not found"}`

---
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

## API Endpoints

| Method | Endpoint | Description | Request Body | Auth Required |
|---|---|---|---|---|
| `GET` | `/` | Health check / Welcome message | *None* | No |
| `POST` | `/register` | Register a new user | JSON (`username`, `password`) | No |
| `POST` | `/login` | Authenticate user and get JWT | Form Data (`username`, `password`) | No |
| `GET` | `/tasks` | Retrieve all tasks for current user | *None* | Yes |
| `POST` | `/tasks` | Create a new task | JSON (`title`, `description`, `completed`) | Yes |
| `GET` | `/tasks/{task_id}` | Retrieve a specific task by ID | *None* | Yes |
| `PUT` | `/tasks/{task_id}` | Update an existing task | JSON (`title`, `description`, `completed`) | Yes |
| `DELETE` | `/tasks/{task_id}` | Delete a task by ID | *None* | Yes |

### Sample Payload (`Task`)

```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, and bread",
  "completed": false
}
```

---
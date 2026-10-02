# Task Management API

A lightweight, robust RESTful API built with **FastAPI** and **PostgreSQL** (using `psycopg`) for managing tasks.

---

## Features

- **CRUD Operations**: Create, read, update, and delete tasks.
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

CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    completed BOOLEAN DEFAULT FALSE
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

| Method | Endpoint | Description | Request Body |
|---|---|---|---|
| `GET` | `/` | Health check / Welcome message | *None* |
| `GET` | `/tasks` | Retrieve all tasks | *None* |
| `POST` | `/tasks` | Create a new task | JSON (`title`, `description`, `completed`) |
| `GET` | `/tasks/{task_id}` | Retrieve a specific task by ID | *None* |
| `PUT` | `/tasks/{task_id}` | Update an existing task | JSON (`title`, `description`, `completed`) |
| `DELETE` | `/tasks/{task_id}` | Delete a task by ID | *None* |

### Sample Payload (`Task`)

```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, and bread",
  "completed": false
}
```

---
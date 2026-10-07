# Task Management System — Project State & Architectural Specification

**Document Version:** 1.0.0  
**Project:** Task Management API & Dashboard  
**Repository:** `Sermystico/backend_practise`  
**Workspace:** `task-management-api`  
**Status:** Operational (Full-Stack MVP+)

---

## 1. Executive Summary & Current State

The **Task Management System** is a secure, full-stack multi-tenant task tracking application. It couples a lightweight, high-performance **FastAPI** backend with a relational **PostgreSQL** database and a zero-dependency **Vanilla JavaScript** single-page application (SPA) featuring a modern dark/light glassmorphic interface.

### Current Maturity Level
- **Backend API:** Fully implemented and functional. Endpoints cover user registration, authentication, and user-isolated CRUD task operations with Pydantic validation.
- **Database:** Normalized relational schema with strict Foreign Key constraints (`ON DELETE CASCADE`) enforcing tenant data isolation.
- **Frontend Client:** Fully integrated SPA with JWT session handling, client-side routing/view switching, real-time filtering, interactive modals, responsive glassmorphic UI, dynamic toast notifications, and celebration animations.
- **Git & Repository Status:** Clean working tree. Recent work focused on enhancing task deletion confirmations, field character limits, UI animations (shutter entrance, confetti), and status quick-filters.

---

## 2. Technology Stack & Ecosystem

```
+-----------------------------------------------------------------------------------+
|                                  CLIENT LAYER                                     |
|  - HTML5 & CSS3 (Glassmorphism, CSS Custom Properties, Dark/Light Theme)         |
|  - Vanilla JavaScript (ES6+, Async/Await, Fetch API, LocalStorage Session)        |
|  - Lucide Icons (CDN) & Google Fonts (Inter)                                     |
|  - HTML5 Canvas Particle Confetti Engine                                          |
+-----------------------------------------------------------------------------------+
                                        |  REST / JSON & URL-Encoded Form
                                        v
+-----------------------------------------------------------------------------------+
|                               APPLICATION LAYER                                   |
|  - Framework: FastAPI (Python 3.10+)                                              |
|  - ASGI Web Server: Uvicorn                                                       |
|  - Authentication: OAuth2 with Password Bearer Token Flow                         |
|  - Cryptography: bcrypt (Salting & Password Hashing), PyJWT (HS256)               |
|  - Validation: Pydantic v2 (Data modeling & Constraints)                          |
|  - Configuration: python-dotenv (.env)                                            |
|  - Documentation: OpenAPI 3.0 / Swagger UI (/docs) & ReDoc (/redoc)              |
+-----------------------------------------------------------------------------------+
                                        |  Direct TCP / Parameterized SQL
                                        v
+-----------------------------------------------------------------------------------+
|                                PERSISTENCE LAYER                                  |
|  - Database: PostgreSQL (Relational)                                             |
|  - Driver: psycopg (v3, Binary)                                                   |
+-----------------------------------------------------------------------------------+
```

### Detailed Component Inventory

| Component | Technology | Version / Specification | Purpose |
|---|---|---|---|
| **API Framework** | [FastAPI](https://fastapi.tiangolo.com/) | Latest | Routing, ASGI application, dependency injection, automatic OpenAPI spec generation |
| **Server Engine** | [Uvicorn](https://www.uvicorn.org/) | Standard ASGI | High-performance asynchronous HTTP server worker |
| **Database Driver** | [psycopg (v3)](https://www.psycopg.org/psycopg3/) | `psycopg[binary]` | Low-overhead PostgreSQL client executing parameterized SQL queries |
| **Database Engine** | [PostgreSQL](https://www.postgresql.org/) | Relational DB | Persistent structured storage for users and tasks |
| **Data Validation** | [Pydantic](https://docs.pydantic.dev/) | `BaseModel`, `Field` | Request body validation, string length constraints, type enforcement |
| **Password Security**| [bcrypt](https://pypi.org/project/bcrypt/) | Standard | Salted password hashing and verification |
| **Token Auth** | [PyJWT](https://pyjwt.readthedocs.io/) | HS256 algorithm | Stateless signed Bearer token generation and decoding |
| **Config Loader** | [python-dotenv](https://github.com/theskumar/python-dotenv) | Standard | Environment variable isolation (`.env`) |
| **Frontend UI** | Vanilla HTML5 / CSS3 / JS | ES6+ Standard | Lightweight SPA; no heavy framework dependencies or build step required |
| **Iconography** | [Lucide Icons](https://lucide.dev/) | Unpkg CDN | Scalable vector UI icons |
| **Design System** | Custom Glassmorphic CSS | Vanilla CSS | Backdrop blur, CSS custom properties, floating gradient orbs, theme toggling |

---

## 3. System Architecture & Codebase Design

The project employs a **modular layered architecture** emphasizing separation of concerns:

```
task-management-api/
├── .env                  # Environment secrets (Git-ignored)
├── .env.example          # Sample environment configuration
├── main.py               # Application entrypoint & HTTP endpoint controllers
├── auth/                 # Authentication & Authorization Domain
│   ├── dependencies.py   # FastAPI dependency for JWT verification (get_current_user)
│   ├── jwt.py            # Token minting and payload encoding
│   ├── models.py         # Pydantic schemas for authentication (User)
│   └── security.py       # Password hashing & verification routines (bcrypt)
├── database/             # Persistence Domain
│   └── db.py             # Database connection & raw SQL CRUD queries
├── frontend/             # Single Page Application Presentation Layer
│   ├── index.html        # SPA DOM structure (Auth, Dashboard, Modals, Canvas)
│   ├── css/
│   │   └── style.css     # Design tokens, themes, animations, glass panels
│   └── js/
│       └── app.js        # State store, API communication, rendering, event handling
└── README.md             # Developer setup and onboarding instructions
```

### Architectural Highlights

1. **Decoupled Security Layer (`auth/`)**:
   - `models.py`: Defines the `User` schema containing username and password.
   - `security.py`: Encapsulates `hash_password` and `verify_password` using `bcrypt` salts.
   - `jwt.py`: Mints signed tokens using HMAC-SHA256 (`HS256`) and a secret key loaded from `.env`.
   - `dependencies.py`: Exposes `get_current_user`, an injectable FastAPI dependency via `OAuth2PasswordBearer(tokenUrl="login")`. Decodes the token and extracts `user_id` and `username`.

2. **Direct Relational Persistence Layer (`database/`)**:
   - Uses `psycopg` direct connections with `autocommit=True` and explicit commit blocks.
   - Strict SQL parameterization (`%s`) across all queries to prevent SQL injection vulnerabilities.
   - Multi-tenant data segregation: Every query querying or altering tasks includes `WHERE user_id = %s`.

3. **Controller & Routing Layer (`main.py`)**:
   - Defines the primary `FastAPI` instance.
   - Injects `CORSMiddleware` with liberal headers/origins for local frontend-backend interoperability.
   - Declares request validation models (e.g., `Task` with title length: 1–100, description length: 1–1000).
   - Maps HTTP methods to service functions with appropriate HTTP error translations (e.g., catching `UniqueViolation` to return 400, returning 401 for bad credentials, 404 for missing entities).

4. **Frontend Architecture (`frontend/`)**:
   - Single Page Application with zero runtime build dependencies.
   - Centralized state management: `token`, `tasks`, `currentFilter`, `currentTheme`.
   - Dynamic UI view swapping (`auth-view` vs `dashboard-view`) based on authentication state.
   - Unified API wrapper (`apiFetch`) providing automatic Bearer token injection and centralized 401 token expiry handling.

---

## 4. Functional Requirements Implemented

### A. Authentication & User Management
- [x] **User Registration (`POST /register`)**:
  - Accepts username and plain-text password.
  - Automatically salts and hashes password before database insertion.
  - Detects duplicate usernames and returns HTTP 400 (`"Username already registered"`).
- [x] **User Login (`POST /login`)**:
  - Implements OAuth2 Password specification using URL-encoded form data (`username`, `password`).
  - Verifies bcrypt password hash against stored hash.
  - Issues signed JWT access token (`{"access_token": "...", "token_type": "bearer"}`).
- [x] **Session Persistence & Route Guarding**:
  - Stores JWT token in client `localStorage`.
  - Automatically loads the dashboard if an active session exists upon page load.
  - Automatically clears state and routes back to authentication screen upon token invalidation or explicit logout.
- [x] **Password Visibility Toggle**:
  - Interactive eye toggle in the login/registration form for user convenience.

### B. Task Lifecycle Management (CRUD)
- [x] **Create Task (`POST /tasks`)**:
  - Validates `title` (1 to 100 characters) and `description` (1 to 1000 characters).
  - Defaults `completed` status to `false`.
  - Automatically associates task with the authenticated user ID extracted from JWT.
  - Frontend supports multiline input (Shift + Enter for new lines, Enter to submit) and auto-expanding textareas.
- [x] **Read All Tasks (`GET /tasks`)**:
  - Retrieves all tasks owned exclusively by the authenticated user.
  - Prevents cross-user data leakage.
- [x] **Read Single Task (`GET /tasks/{task_id}`)**:
  - Fetches specific task by ID with strict `user_id` validation.
  - Powers the frontend "View Task Details" modal dialog.
- [x] **Update Task (`PUT /tasks/{task_id}`)**:
  - Allows full edits to title, description, and completion state.
  - Verifies task ownership before updating; returns HTTP 404 if not found or unauthorized.
- [x] **Delete Task (`DELETE /tasks/{task_id}`)**:
  - Hard deletes task with confirmation.
  - Frontend features a custom confirmation modal with exit animations.
- [x] **Quick Status Toggles**:
  - One-click Mark Complete (`PUT` updating `completed = true`).
  - One-click Reopen / Incomplete (`PUT` updating `completed = false`).
  - "Complete & Delete" quick combo workflow with safety confirmation.

### C. Dashboard & User Experience (UX)
- [x] **Real-Time KPI Counters**:
  - Live metric widgets displaying: **Total Tasks**, **Active Tasks**, and **Completed Tasks**.
  - Clicking any KPI card automatically filters the list accordingly.
- [x] **View Filtering & Navigation**:
  - Tabbed sidebar navigation: **All Tasks**, **Active**, and **Completed**.
  - Client-side sorting: Incomplete tasks appear first, followed by completed tasks; sorted newest first by ID.
  - Automatic task serial numbers (`#1`, `#2`, etc.).
- [x] **Personalized Header**:
  - Time-aware contextual greeting ("Good morning", "Good afternoon", "Good evening").
- [x] **Visual Feedback & Gamification**:
  - Toast Notification System (slide-in top-right alerts for Success, Error, and Info).
  - HTML5 Canvas Confetti animation triggered upon task completion.
  - Custom Shutter intro screen animation upon page load.
- [x] **Theme System**:
  - Full Dark Mode and Light Mode support with smooth CSS transitions.
  - Preference saved and restored via `localStorage`.

---

## 5. Database Schema & Data Models

### Physical Schema (PostgreSQL)

```sql
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

### Relational Integrity
- **1-to-Many Relationship**: One `User` can own zero, one, or many `Tasks`.
- **Cascade Deletion**: If a user is deleted, all corresponding tasks are deleted automatically via `ON DELETE CASCADE`.
- **Unique Constraint**: `users.username` is unique, indexed by default in PostgreSQL.

---

## 6. API Endpoint Reference

| Method | Route | Description | Auth Required | Request Payload | Response |
|---|---|---|:---:|---|---|
| `GET` | `/` | API health check & status probe | No | *None* | `{"message": "..."}` |
| `POST` | `/register` | Register new user account | No | JSON: `{ username, password }` | `[id, username]` |
| `POST` | `/login` | Authenticate & retrieve JWT token | No | Form Data: `username`, `password` | `{"access_token": "...", "token_type": "bearer"}` |
| `GET` | `/tasks` | List all tasks of authenticated user | **Yes** | *None* | Array of tasks: `[[id, title, desc, done, user_id], ...]` |
| `POST` | `/tasks` | Create new task for user | **Yes** | JSON: `{ title, description, completed }` | `[id, title, desc, done, user_id]` |
| `GET` | `/tasks/{id}` | Retrieve specific task | **Yes** | *None* | `[id, title, desc, done, user_id]` |
| `PUT` | `/tasks/{id}` | Update task title, description, or status | **Yes** | JSON: `{ title, description, completed }` | `[id, title, desc, done, user_id]` |
| `DELETE` | `/tasks/{id}`| Remove task | **Yes** | *None* | `{"message": "Task deleted"}` |

---

## 7. Current Project Observations & Recommended Next Steps

While the application is fully functional and responsive, the following improvements can guide future sprints:

1. **Database Connection Pooling**:
   - Currently, `database/db.py` creates a single static `conn = psycopg.connect(...)` at startup.
   - *Recommendation:* Upgrade to `psycopg_pool.ConnectionPool` or FastAPI lifecycle events (`lifespan`) to handle concurrent database requests gracefully without socket conflicts.

2. **Pydantic Response Models**:
   - The API currently returns raw tuples from database cursors (e.g., `(id, title, description, ...)`) which the frontend maps by index.
   - *Recommendation:* Convert cursor outputs to dictionaries or Pydantic schemas (`TaskOut`, `UserOut`) to deliver clear JSON keys (`{ "id": 1, "title": "..." }`) rather than index arrays.

3. **JWT Expiration & Refresh Strategy**:
   - The generated JWT access token does not define an `exp` (expiration) claim in `auth/jwt.py`.
   - *Recommendation:* Add an expiration window (e.g., 30–60 minutes) and optionally implement refresh tokens for enhanced credential hygiene.

4. **Testing & Automation**:
   - Add automated test coverage with `pytest` and `httpx` to validate authentication workflows and multi-tenant isolation in CI/CD.

import pytest
from fastapi.testclient import TestClient
from main import app
import psycopg
import os

client = TestClient(app)

# Helper functions to clear the database for tests
def clear_db():
    try:
        conn = psycopg.connect(
            host=os.getenv("DB_HOST", "localhost"),
            dbname=os.getenv("DB_NAME", "task_management"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres"),
            autocommit=True
        )
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE users CASCADE;")
        conn.close()
    except Exception as e:
        print("DB connect error:", e)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    clear_db()
    yield
    clear_db()

def test_registration_and_login():
    # 1. Register User A
    response = client.post("/register", json={"username": "userA", "password": "passwordA"})
    assert response.status_code == 200
    assert response.json()[1] == "userA"

    # 2. Duplicate registration fails
    response = client.post("/register", json={"username": "userA", "password": "passwordA"})
    assert response.status_code == 400

    # 3. Login User A
    response = client.post("/login", data={"username": "userA", "password": "passwordA"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token is not None

def test_task_isolation():
    # Setup User A
    client.post("/register", json={"username": "userA", "password": "passwordA"})
    token_a = client.post("/login", data={"username": "userA", "password": "passwordA"}).json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Setup User B
    client.post("/register", json={"username": "userB", "password": "passwordB"})
    token_b = client.post("/login", data={"username": "userB", "password": "passwordB"}).json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A creates a task
    res_a = client.post("/tasks", json={"title": "Task A", "description": "Desc A", "completed": False}, headers=headers_a)
    task_a_id = res_a.json()["id"]

    # User B creates a task
    res_b = client.post("/tasks", json={"title": "Task B", "description": "Desc B", "completed": False}, headers=headers_b)
    task_b_id = res_b.json()["id"]

    # User A retrieves tasks, should only see Task A
    res_get_a = client.get("/tasks", headers=headers_a)
    tasks_a = res_get_a.json()
    assert len(tasks_a) == 1
    assert tasks_a[0]["id"] == task_a_id

    # User A tries to get User B's task
    res_get_b_by_a = client.get(f"/tasks/{task_b_id}", headers=headers_a)
    assert res_get_b_by_a.status_code == 404

    # User A tries to update User B's task
    res_update_b_by_a = client.put(f"/tasks/{task_b_id}", json={"title": "Hacked", "description": "Hacked", "completed": True}, headers=headers_a)
    assert res_update_b_by_a.status_code == 404

    # User A tries to delete User B's task
    res_delete_b_by_a = client.delete(f"/tasks/{task_b_id}", headers=headers_a)
    assert res_delete_b_by_a.status_code == 404

def test_task_crud():
    # Setup User
    client.post("/register", json={"username": "testuser", "password": "testpassword"})
    token = client.post("/login", data={"username": "testuser", "password": "testpassword"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create
    res_create = client.post("/tasks", json={"title": "Buy Milk", "description": "2 liters", "completed": False}, headers=headers)
    assert res_create.status_code == 200
    task_id = res_create.json()["id"]

    # Read
    res_read = client.get(f"/tasks/{task_id}", headers=headers)
    assert res_read.status_code == 200
    assert res_read.json()["title"] == "Buy Milk"

    # Update
    res_update = client.put(f"/tasks/{task_id}", json={"title": "Buy Milk", "description": "2 liters", "completed": True}, headers=headers)
    assert res_update.status_code == 200
    assert res_update.json()["completed"] == True

    # Delete
    res_delete = client.delete(f"/tasks/{task_id}", headers=headers)
    assert res_delete.status_code == 200

    # Read again -> 404
    res_read_after = client.get(f"/tasks/{task_id}", headers=headers)
    assert res_read_after.status_code == 404

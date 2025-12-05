import uuid
from fastapi.testclient import TestClient

def test_create_user_success(client: TestClient):
    """Test successful user creation."""
    response = client.post("/users/", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
        "role": "master"
    }, headers={"Idempotency-Key": str(uuid.uuid4())})
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_create_user_duplicate_username(client: TestClient):
    """Test user creation with a duplicate username."""
    # Create a user first
    response = client.post("/users/", json={
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "password123",
        "role": "master"
    }, headers={"Idempotency-Key": str(uuid.uuid4())})
    assert response.status_code == 201

    # Try to create another user with the same username
    response = client.post("/users/", json={
        "username": "testuser2",
        "email": "test3@example.com",
        "password": "password456",
        "role": "master"  # Виправлено на валідну роль
    }, headers={"Idempotency-Key": str(uuid.uuid4())})
    assert response.status_code == 400
    assert "Username already registered" in response.text
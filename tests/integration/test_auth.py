"""Integration tests for authentication endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from scheduler.api.main import app
from scheduler.db import get_session


@pytest.fixture(name="session")
def session_fixture():
    """Create a fresh in-memory database for each test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with a fresh database session."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestSignup:
    """Test signup endpoint."""

    def test_signup_creates_user(self, client: TestClient):
        """POST /auth/signup creates user and returns token."""
        response = client.post("/auth/signup", json={
            "username": "admin",
            "email": "admin@example.com",
            "password": "secret123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_signup_duplicate_username(self, client: TestClient):
        """POST /auth/signup rejects duplicate username."""
        client.post("/auth/signup", json={
            "username": "admin",
            "email": "admin1@example.com",
            "password": "secret123"
        })
        
        response = client.post("/auth/signup", json={
            "username": "admin",
            "email": "admin2@example.com",
            "password": "secret456"
        })
        
        assert response.status_code == 400
        assert "Username already registered" in response.json()["detail"]


class TestLogin:
    """Test login endpoint."""

    def test_login_success(self, client: TestClient):
        """POST /auth/login returns token for valid credentials."""
        # First signup
        client.post("/auth/signup", json={
            "username": "admin",
            "email": "admin@example.com",
            "password": "secret123"
        })
        
        # Then login
        response = client.post("/auth/login", data={
            "username": "admin",
            "password": "secret123"
        })
        
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_wrong_password(self, client: TestClient):
        """POST /auth/login rejects wrong password."""
        client.post("/auth/signup", json={
            "username": "admin",
            "email": "admin@example.com",
            "password": "secret123"
        })
        
        response = client.post("/auth/login", data={
            "username": "admin",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401


class TestGetMe:
    """Test /auth/me endpoint."""

    def test_get_me_authenticated(self, client: TestClient):
        """GET /auth/me returns user info with valid token."""
        # Signup and get token
        signup_resp = client.post("/auth/signup", json={
            "username": "admin",
            "email": "admin@example.com",
            "password": "secret123"
        })
        token = signup_resp.json()["access_token"]
        
        # Get current user
        response = client.get("/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        assert data["email"] == "admin@example.com"
        assert data["is_admin"] is True

    def test_get_me_no_token(self, client: TestClient):
        """GET /auth/me returns 401 without token."""
        response = client.get("/auth/me")
        assert response.status_code == 401

"""Integration tests for schedule view endpoints."""

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


class TestScheduleViews:
    """Test schedule query endpoints."""

    def test_get_professor_schedule(self, client: TestClient):
        """GET /schedules/professor/{id} returns professor's courses."""
        # Arrange: create professor, classroom, and courses
        client.post("/courses/professors", json={"id": "prof-001", "name": "Alice"})
        client.post("/courses/classrooms", json={"id": "room-101", "name": "Room 101", "capacity": 50})
        client.post("/courses/", json={
            "id": "cs501", "name": "ML", "professor_id": "prof-001",
            "classroom_id": "room-101", "timeslot": {"weekday": 1, "period": 1}
        })
        client.post("/courses/", json={
            "id": "cs502", "name": "DL", "professor_id": "prof-001",
            "classroom_id": "room-101", "timeslot": {"weekday": 2, "period": 2}
        })

        # Act
        response = client.get("/courses/schedules/professor/prof-001")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "professor" in data
        assert data["professor"]["id"] == "prof-001"
        assert "courses" in data
        assert data["total"] == 2

    def test_get_professor_schedule_not_found(self, client: TestClient):
        """GET /schedules/professor/{id} returns 404 for invalid ID."""
        response = client.get("/courses/schedules/professor/nonexistent")
        assert response.status_code == 404

    def test_get_classroom_schedule(self, client: TestClient):
        """GET /schedules/classroom/{id} returns classroom's courses."""
        # Arrange
        client.post("/courses/professors", json={"id": "prof-001", "name": "Alice"})
        client.post("/courses/classrooms", json={"id": "room-101", "name": "Room 101", "capacity": 50})
        client.post("/courses/", json={
            "id": "cs501", "name": "ML", "professor_id": "prof-001",
            "classroom_id": "room-101", "timeslot": {"weekday": 1, "period": 1}
        })

        # Act
        response = client.get("/courses/schedules/classroom/room-101")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "classroom" in data
        assert data["classroom"]["id"] == "room-101"
        assert data["total"] == 1

    def test_get_weekly_schedule(self, client: TestClient):
        """GET /schedules/weekly returns full grid."""
        # Arrange
        client.post("/courses/professors", json={"id": "prof-001", "name": "Alice"})
        client.post("/courses/classrooms", json={"id": "room-101", "name": "Room 101", "capacity": 50})
        client.post("/courses/", json={
            "id": "cs501", "name": "ML", "professor_id": "prof-001",
            "classroom_id": "room-101", "timeslot": {"weekday": 1, "period": 1}
        })

        # Act
        response = client.get("/courses/schedules/weekly")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "grid" in data
        assert "total_courses" in data


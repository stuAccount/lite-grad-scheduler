"""API integration tests - Testing full request/response cycle."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from scheduler.api.main import app
from scheduler.db import get_session


# Create in-memory database for testing
@pytest.fixture(name="session")
def session_fixture():
    """Create a fresh test database for each test."""
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
    """FastAPI test client with overridden database session."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestRootEndpoint:
    """Test the root API endpoint."""

    def test_root(self, client: TestClient):
        """GET / returns API information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data


class TestProfessorEndpoints:
    """Test professor management endpoints."""

    def test_create_professor(self, client: TestClient):
        """POST /courses/professors creates a new professor."""
        response = client.post(
            "/courses/professors",
            json={"id": "prof-001", "name": "Alice Wang"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == "prof-001"
        assert data["name"] == "Alice Wang"


class TestClassroomEndpoints:
    """Test classroom management endpoints."""

    def test_create_classroom(self, client: TestClient):
        """POST /courses/classrooms creates a new classroom."""
        response = client.post(
            "/courses/classrooms",
            json={"id": "room-101", "name": "Room 101", "capacity": 50}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == "room-101"
        assert data["capacity"] == 50


class TestCourseEndpoints:
    """Test course management and conflict detection endpoints."""

    def test_create_course(self, client: TestClient):
        """POST /courses creates a new course."""
        # First create dependencies
        client.post(
            "/courses/professors",
            json={"id": "prof-001", "name": "Alice Wang"}
        )
        client.post(
            "/courses/classrooms",
            json={"id": "room-101", "name": "Room 101", "capacity": 50}
        )

        # Create course
        response = client.post(
            "/courses/",
            json={
                "id": "cs501",
                "name": "Machine Learning",
                "professor_id": "prof-001",
                "classroom_id": "room-101",
                "timeslot": {"weekday": 1, "period": 1}
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == "cs501"
        assert data["name"] == "Machine Learning"
        assert data["weekday"] == 1
        assert data["period"] == 1

    def test_list_courses(self, client: TestClient):
        """GET /courses returns all courses."""
        # Create professor and classroom
        client.post(
            "/courses/professors",
            json={"id": "prof-001", "name": "Alice Wang"}
        )
        client.post(
            "/courses/classrooms",
            json={"id": "room-101", "name": "Room 101", "capacity": 50}
        )

        # Create courses
        client.post(
            "/courses/",
            json={
                "id": "cs501",
                "name": "Machine Learning",
                "professor_id": "prof-001",
                "classroom_id": "room-101",
                "timeslot": {"weekday": 1, "period": 1}
            }
        )
        client.post(
            "/courses/",
            json={
                "id": "cs502",
                "name": "Deep Learning",
                "professor_id": "prof-001",
                "classroom_id": "room-101",
                "timeslot": {"weekday": 1, "period": 2}
            }
        )

        # List courses
        response = client.get("/courses/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_check_conflicts_no_conflicts(self, client: TestClient):
        """POST /courses/check-conflicts with no conflicts."""
        # Setup
        client.post(
            "/courses/professors",
            json={"id": "prof-001", "name": "Alice Wang"}
        )
        client.post(
            "/courses/classrooms",
            json={"id": "room-101", "name": "Room 101", "capacity": 50}
        )
        client.post(
            "/courses/",
            json={
                "id": "cs501",
                "name": "Machine Learning",
                "professor_id": "prof-001",
                "classroom_id": "room-101",
                "timeslot": {"weekday": 1, "period": 1}
            }
        )
        client.post(
            "/courses/",
            json={
                "id": "cs502",
                "name": "Deep Learning",
                "professor_id": "prof-001",
                "classroom_id": "room-101",
                "timeslot": {"weekday": 1, "period": 2}  # Different periods
            }
        )

        # Check conflicts
        response = client.post("/courses/check-conflicts")
        assert response.status_code == 200
        data = response.json()
        assert data["professor_conflicts"] == 0
        assert data["classroom_conflicts"] == 0

    def test_check_conflicts_with_professor_conflict(self, client: TestClient):
        """POST /courses/check-conflicts detects professor double-booking."""
        # Setup
        client.post(
            "/courses/professors",
            json={"id": "prof-001", "name": "Alice Wang"}
        )
        client.post(
            "/courses/classrooms",
            json={"id": "room-101", "name": "Room 101", "capacity": 50}
        )
        client.post(
            "/courses/classrooms",
            json={"id": "room-202", "name": "Room 202", "capacity": 100}
        )

        # Create conflicting courses (same professor, same timeslot, different rooms)
        client.post(
            "/courses/",
            json={
                "id": "cs501",
                "name": "Machine Learning",
                "professor_id": "prof-001",
                "classroom_id": "room-101",
                "timeslot": {"weekday": 1, "period": 1}
            }
        )
        client.post(
            "/courses/",
            json={
                "id": "cs502",
                "name": "Deep Learning",
                "professor_id": "prof-001",
                "classroom_id": "room-202",
                "timeslot": {"weekday": 1, "period": 1}  # SAME timeslot!
            }
        )

        # Check conflicts
        response = client.post("/courses/check-conflicts")
        assert response.status_code == 200
        data = response.json()
        assert data["professor_conflicts"] == 1
        assert len(data["details"]["professor_conflicts"]) == 1

    def test_check_conflicts_with_classroom_conflict(self, client: TestClient):
        """POST /courses/check-conflicts detects classroom double-booking."""
        # Setup
        client.post(
            "/courses/professors",
            json={"id": "prof-001", "name": "Alice Wang"}
        )
        client.post(
            "/courses/professors",
            json={"id": "prof-002", "name": "Bob Chen"}
        )
        client.post(
            "/courses/classrooms",
            json={"id": "room-101", "name": "Room 101", "capacity": 50}
        )

        # Create conflicting courses (different professors, same room, same timeslot)
        client.post(
            "/courses/",
            json={
                "id": "cs501",
                "name": "Machine Learning",
                "professor_id": "prof-001",
                "classroom_id": "room-101",
                "timeslot": {"weekday": 1, "period": 1}
            }
        )
        client.post(
            "/courses/",
            json={
                "id": "cs601",
                "name": "Database Systems",
                "professor_id": "prof-002",
                "classroom_id": "room-101",
                "timeslot": {"weekday": 1, "period": 1}  # SAME timeslot!
            }
        )

        # Check conflicts
        response = client.post("/courses/check-conflicts")
        assert response.status_code == 200
        data = response.json()
        assert data["classroom_conflicts"] == 1
        assert len(data["details"]["classroom_conflicts"]) == 1

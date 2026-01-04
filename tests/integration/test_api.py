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


def get_auth_headers() -> dict:
    """Generate auth headers for protected API calls."""
    from scheduler.services.security import create_access_token
    token = create_access_token({"sub": "test-user"})
    return {"Authorization": f"Bearer {token}"}


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
            headers=get_auth_headers(),
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
            headers=get_auth_headers(),
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
            headers=get_auth_headers(),
            json={"id": "prof-001", "name": "Alice Wang"}
        )
        client.post(
            "/courses/classrooms",
            headers=get_auth_headers(),
            json={"id": "room-101", "name": "Room 101", "capacity": 50}
        )

        # Create course
        response = client.post(
            "/courses/",
            headers=get_auth_headers(),
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
            headers=get_auth_headers(),
            json={"id": "prof-001", "name": "Alice Wang"}
        )
        client.post(
            "/courses/classrooms",
            headers=get_auth_headers(),
            json={"id": "room-101", "name": "Room 101", "capacity": 50}
        )

        # Create courses
        client.post(
            "/courses/",
            headers=get_auth_headers(),
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
            headers=get_auth_headers(),
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
            headers=get_auth_headers(),
            json={"id": "prof-001", "name": "Alice Wang"}
        )
        client.post(
            "/courses/classrooms",
            headers=get_auth_headers(),
            json={"id": "room-101", "name": "Room 101", "capacity": 50}
        )
        client.post(
            "/courses/",
            headers=get_auth_headers(),
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
            headers=get_auth_headers(),
            json={
                "id": "cs502",
                "name": "Deep Learning",
                "professor_id": "prof-001",
                "classroom_id": "room-101",
                "timeslot": {"weekday": 1, "period": 2}  # Different periods
            }
        )

        # Check conflicts
        response = client.post("/courses/check-conflicts", headers=get_auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert data["professor_conflicts"] == 0
        assert data["classroom_conflicts"] == 0

    def test_check_conflicts_with_professor_conflict(self, client: TestClient):
        """POST /courses/check-conflicts detects professor double-booking."""
        # Setup
        client.post(
            "/courses/professors",
            headers=get_auth_headers(),
            json={"id": "prof-001", "name": "Alice Wang"}
        )
        client.post(
            "/courses/classrooms",
            headers=get_auth_headers(),
            json={"id": "room-101", "name": "Room 101", "capacity": 50}
        )
        client.post(
            "/courses/classrooms",
            headers=get_auth_headers(),
            json={"id": "room-202", "name": "Room 202", "capacity": 100}
        )

        # Create conflicting courses (same professor, same timeslot, different rooms)
        client.post(
            "/courses/",
            headers=get_auth_headers(),
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
            headers=get_auth_headers(),
            json={
                "id": "cs502",
                "name": "Deep Learning",
                "professor_id": "prof-001",
                "classroom_id": "room-202",
                "timeslot": {"weekday": 1, "period": 1}  # SAME timeslot!
            }
        )

        # Check conflicts
        response = client.post("/courses/check-conflicts", headers=get_auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert data["professor_conflicts"] == 1
        assert len(data["details"]["professor_conflicts"]) == 1

    def test_check_conflicts_with_classroom_conflict(self, client: TestClient):
        """POST /courses/check-conflicts detects classroom double-booking."""
        # Setup
        client.post(
            "/courses/professors",
            headers=get_auth_headers(),
            json={"id": "prof-001", "name": "Alice Wang"}
        )
        client.post(
            "/courses/professors",
            headers=get_auth_headers(),
            json={"id": "prof-002", "name": "Bob Chen"}
        )
        client.post(
            "/courses/classrooms",
            headers=get_auth_headers(),
            json={"id": "room-101", "name": "Room 101", "capacity": 50}
        )

        # Create conflicting courses (different professors, same room, same timeslot)
        client.post(
            "/courses/",
            headers=get_auth_headers(),
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
            headers=get_auth_headers(),
            json={
                "id": "cs601",
                "name": "Database Systems",
                "professor_id": "prof-002",
                "classroom_id": "room-101",
                "timeslot": {"weekday": 1, "period": 1}  # SAME timeslot!
            }
        )

        # Check conflicts
        response = client.post("/courses/check-conflicts", headers=get_auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert data["classroom_conflicts"] == 1
        assert len(data["details"]["classroom_conflicts"]) == 1


class TestScheduleGeneration:
    """Test automated schedule generation endpoints."""

    def test_generate_schedule(self, client: TestClient):
        """POST /courses/schedules/generate creates conflict-free schedule."""
        # Create professors and classrooms
        client.post(
            "/courses/professors",
            headers=get_auth_headers(),
            json={"id": "prof-001", "name": "Alice Wang"}
        )
        client.post(
            "/courses/professors",
            headers=get_auth_headers(),
            json={"id": "prof-002", "name": "Bob Chen"}
        )
        client.post(
            "/courses/classrooms",
            headers=get_auth_headers(),
            json={"id": "room-101", "name": "Room 101", "capacity": 50}
        )
        client.post(
            "/courses/classrooms",
            headers=get_auth_headers(),
            json={"id": "room-202", "name": "Room 202", "capacity": 100}
        )

        # Generate schedule
        response = client.post(
            "/courses/schedules/generate",
            headers=get_auth_headers(),
            json={
                "course_requests": [
                    {
                        "id": "cs501",
                        "name": "Machine Learning",
                        "professor_id": "prof-001",
                        "classroom_id": "room-101"
                    },
                    {
                        "id": "cs502",
                        "name": "Deep Learning",
                        "professor_id": "prof-001",
                        "classroom_id": "room-202"
                    },
                    {
                        "id": "cs601",
                        "name": "Database Systems",
                        "professor_id": "prof-002",
                        "classroom_id": "room-101"
                    }
                ]
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Schedule generated successfully"
        assert data["total"] == 3
        assert len(data["courses"]) == 3

        # Verify all courses have timeslots
        for course in data["courses"]:
            assert "weekday" in course
            assert "period" in course
            assert course["weekday"] >= 1 and course["weekday"] <= 5
            assert course["period"] >= 1 and course["period"] <= 12

        # Verify schedule is conflict-free
        conflict_response = client.post("/courses/check-conflicts", headers=get_auth_headers())
        assert conflict_response.status_code == 200
        conflict_data = conflict_response.json()
        assert conflict_data["professor_conflicts"] == 0
        assert conflict_data["classroom_conflicts"] == 0


class TestValidation:
    """Test referential integrity validation."""

    def test_create_course_with_nonexistent_professor(self, client: TestClient):
        """POST /courses with invalid professor_id returns 404."""
        # Create only a classroom, no professor
        client.post(
            "/courses/classrooms",
            headers=get_auth_headers(),
            json={"id": "room-101", "name": "Room 101", "capacity": 50}
        )

        # Try to create course with non-existent professor
        response = client.post(
            "/courses/",
            headers=get_auth_headers(),
            json={
                "id": "cs501",
                "name": "Machine Learning",
                "professor_id": "invalid-prof",
                "classroom_id": "room-101",
                "timeslot": {"weekday": 1, "period": 1}
            }
        )

        assert response.status_code == 404
        data = response.json()
        assert "professor" in data["detail"].lower()

    def test_create_course_with_nonexistent_classroom(self, client: TestClient):
        """POST /courses with invalid classroom_id returns 404."""
        # Create only a professor, no classroom
        client.post(
            "/courses/professors",
            headers=get_auth_headers(),
            json={"id": "prof-001", "name": "Alice Wang"}
        )

        # Try to create course with non-existent classroom
        response = client.post(
            "/courses/",
            headers=get_auth_headers(),
            json={
                "id": "cs501",
                "name": "Machine Learning",
                "professor_id": "prof-001",
                "classroom_id": "invalid-room",
                "timeslot": {"weekday": 1, "period": 1}
            }
        )

        assert response.status_code == 404
        data = response.json()
        assert "classroom" in data["detail"].lower()

    def test_create_course_with_both_invalid(self, client: TestClient):
        """POST /courses with both IDs invalid returns 404."""
        # Create nothing
        response = client.post(
            "/courses/",
            headers=get_auth_headers(),
            json={
                "id": "cs501",
                "name": "Machine Learning",
                "professor_id": "invalid-prof",
                "classroom_id": "invalid-room",
                "timeslot": {"weekday": 1, "period": 1}
            }
        )

        assert response.status_code == 404
        # Should mention at least one of the missing resources
        data = response.json()
        detail_lower = data["detail"].lower()
        assert "professor" in detail_lower or "classroom" in detail_lower

    def test_generate_schedule_with_invalid_professor(self, client: TestClient):
        """POST /courses/schedules/generate with invalid professor_id returns 404."""
        # Create only classrooms
        client.post(
            "/courses/classrooms",
            headers=get_auth_headers(),
            json={"id": "room-101", "name": "Room 101", "capacity": 50}
        )

        # Try to generate schedule with non-existent professor
        response = client.post(
            "/courses/schedules/generate",
            headers=get_auth_headers(),
            json={
                "course_requests": [
                    {
                        "id": "cs501",
                        "name": "Machine Learning",
                        "professor_id": "invalid-prof",
                        "classroom_id": "room-101"
                    }
                ]
            }
        )

        assert response.status_code == 404
        data = response.json()
        assert "professor" in data["detail"].lower()

    def test_generate_schedule_with_invalid_classroom(self, client: TestClient):
        """POST /courses/schedules/generate with invalid classroom_id returns 404."""
        # Create only professors
        client.post(
            "/courses/professors",
            headers=get_auth_headers(),
            json={"id": "prof-001", "name": "Alice Wang"}
        )

        # Try to generate schedule with non-existent classroom
        response = client.post(
            "/courses/schedules/generate",
            headers=get_auth_headers(),
            json={
                "course_requests": [
                    {
                        "id": "cs501",
                        "name": "Machine Learning",
                        "professor_id": "prof-001",
                        "classroom_id": "invalid-room"
                    }
                ]
            }
        )

        assert response.status_code == 404
        data = response.json()
        assert "classroom" in data["detail"].lower()

class TestScheduleViews:
    """Test schedule query endpoints."""

    def test_get_professor_schedule(self, client: TestClient):
        """GET /schedules/professor/{id} returns professor's courses."""
        # Arrange: create professor, classroom, and courses

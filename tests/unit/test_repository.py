"""Unit tests for CourseRepository."""

import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from scheduler.db.repository import CourseRepository
from scheduler.domain.models import Professor, Classroom


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


class TestProfessorLookup:
    """Test professor lookup methods."""

    def test_get_professor_by_id_found(self, session: Session):
        """get_professor_by_id returns professor when ID exists."""
        # Arrange
        repo = CourseRepository(session)
        professor = Professor(id="prof-001", name="Alice Wang")
        repo.add_professor(professor)

        # Act
        result = repo.get_professor_by_id("prof-001")

        # Assert
        assert result is not None
        assert result.id == "prof-001"
        assert result.name == "Alice Wang"

    def test_get_professor_by_id_not_found(self, session: Session):
        """get_professor_by_id returns None when ID doesn't exist."""
        # Arrange
        repo = CourseRepository(session)

        # Act
        result = repo.get_professor_by_id("nonexistent-id")

        # Assert
        assert result is None


class TestClassroomLookup:
    """Test classroom lookup methods."""

    def test_get_classroom_by_id_found(self, session: Session):
        """get_classroom_by_id returns classroom when ID exists."""
        # Arrange
        repo = CourseRepository(session)
        classroom = Classroom(id="room-101", name="Room 101", capacity=50)
        repo.add_classroom(classroom)

        # Act
        result = repo.get_classroom_by_id("room-101")

        # Assert
        assert result is not None
        assert result.id == "room-101"
        assert result.name == "Room 101"
        assert result.capacity == 50

    def test_get_classroom_by_id_not_found(self, session: Session):
        """get_classroom_by_id returns None when ID doesn't exist."""
        # Arrange
        repo = CourseRepository(session)

        # Act
        result = repo.get_classroom_by_id("nonexistent-id")

        # Assert
        assert result is None

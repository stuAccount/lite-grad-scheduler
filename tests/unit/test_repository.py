"""Unit tests for CourseRepository."""

import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from scheduler.db.repository import CourseRepository
from scheduler.domain.models import Professor, Classroom, Course


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


class TestCourseQueries:
    """Test course query methods."""

    def test_get_courses_by_professor(self, session: Session):
        """get_courses_by_professor returns courses for specific professor."""
        # Arrange
        repo = CourseRepository(session)
        from scheduler.domain.models import Weekday, TimeSlot
        
        prof1 = Professor(id="prof-001", name="Alice")
        prof2 = Professor(id="prof-002", name="Bob")
        classroom = Classroom(id="room-101", name="Room 101", capacity=50)
        repo.add_professor(prof1)
        repo.add_professor(prof2)
        repo.add_classroom(classroom)

        course1 = Course.from_timeslot(
            id="cs501", name="ML", professor_id="prof-001",
            classroom_id="room-101", timeslot=TimeSlot(Weekday.MONDAY, 1)
        )
        course2 = Course.from_timeslot(
            id="cs502", name="DL", professor_id="prof-001",
            classroom_id="room-101", timeslot=TimeSlot(Weekday.TUESDAY, 2)
        )
        course3 = Course.from_timeslot(
            id="cs601", name="DB", professor_id="prof-002",
            classroom_id="room-101", timeslot=TimeSlot(Weekday.WEDNESDAY, 3)
        )
        repo.add_course(course1)
        repo.add_course(course2)
        repo.add_course(course3)

        # Act
        result = repo.get_courses_by_professor("prof-001")

        # Assert
        assert len(result) == 2
        assert all(c.professor_id == "prof-001" for c in result)
        course_ids = {c.id for c in result}
        assert course_ids == {"cs501", "cs502"}

    def test_get_courses_by_classroom(self, session: Session):
        """get_courses_by_classroom returns courses for specific classroom."""
        # Arrange
        repo = CourseRepository(session)
        from scheduler.domain.models import Weekday, TimeSlot
        
        prof = Professor(id="prof-001", name="Alice")
        room1 = Classroom(id="room-101", name="Room 101", capacity=50)
        room2 = Classroom(id="room-202", name="Room 202", capacity=100)
        repo.add_professor(prof)
        repo.add_classroom(room1)
        repo.add_classroom(room2)

        course1 = Course.from_timeslot(
            id="cs501", name="ML", professor_id="prof-001",
            classroom_id="room-101", timeslot=TimeSlot(Weekday.MONDAY, 1)
        )
        course2 = Course.from_timeslot(
            id="cs502", name="DL", professor_id="prof-001",
            classroom_id="room-202", timeslot=TimeSlot(Weekday.TUESDAY, 2)
        )
        repo.add_course(course1)
        repo.add_course(course2)

        # Act
        result = repo.get_courses_by_classroom("room-101")

        # Assert
        assert len(result) == 1
        assert result[0].id == "cs501"
        assert result[0].classroom_id == "room-101"

    def test_get_all_courses_ordered(self, session: Session):
        """get_all_courses_ordered returns courses sorted by weekday and period."""
        # Arrange
        repo = CourseRepository(session)
        from scheduler.domain.models import Weekday, TimeSlot
        
        prof = Professor(id="prof-001", name="Alice")
        classroom = Classroom(id="room-101", name="Room 101", capacity=50)
        repo.add_professor(prof)
        repo.add_classroom(classroom)

        # Add courses in random order
        course_wed = Course.from_timeslot(
            id="cs601", name="DB", professor_id="prof-001",
            classroom_id="room-101", timeslot=TimeSlot(Weekday.WEDNESDAY, 1)
        )
        course_mon = Course.from_timeslot(
            id="cs501", name="ML", professor_id="prof-001",
            classroom_id="room-101", timeslot=TimeSlot(Weekday.MONDAY, 2)
        )
        course_tue = Course.from_timeslot(
            id="cs502", name="DL", professor_id="prof-001",
            classroom_id="room-101", timeslot=TimeSlot(Weekday.TUESDAY, 1)
        )
        repo.add_course(course_wed)
        repo.add_course(course_mon)
        repo.add_course(course_tue)

        # Act
        result = repo.get_all_courses_ordered()

        # Assert
        assert len(result) == 3
        # Check ordering: Monday, Tuesday, Wednesday
        assert result[0].id == "cs501"  # Monday period 2
        assert result[1].id == "cs502"  # Tuesday period 1
        assert result[2].id == "cs601"  # Wednesday period 1


"""TDD tests for ConflictDetector - Hard constraint detection.

Business Rules (Hard Constraints):
1. A Professor cannot be assigned to two courses at the same TimeSlot.
2. A Classroom cannot host two courses at the same TimeSlot.
"""

import pytest

from scheduler.domain.models import Classroom, Course, Professor, TimeSlot
from scheduler.services.conflict_detector import ConflictDetector


class TestProfessorConflict:
    """Test suite: A Professor cannot teach two courses at the same TimeSlot."""

    @pytest.fixture
    def detector(self) -> ConflictDetector:
        return ConflictDetector()

    def test_no_conflict_when_professor_teaches_at_different_timeslots(
        self,
        detector: ConflictDetector,
        professor_alice: Professor,
        classroom_101: Classroom,
        classroom_202: Classroom,
        monday_period_1: TimeSlot,
        monday_period_2: TimeSlot,
    ) -> None:
        """GIVEN Alice teaches two courses at different timeslots
        WHEN we check for professor conflicts
        THEN no conflicts should be found
        """
        course_a = Course.from_timeslot(
            id="course-001",
            name="Machine Learning",
            professor_id=professor_alice.id,
            classroom_id=classroom_101.id,
            timeslot=monday_period_1,
        )
        course_b = Course.from_timeslot(
            id="course-002",
            name="Deep Learning",
            professor_id=professor_alice.id,
            classroom_id=classroom_202.id,
            timeslot=monday_period_2,  # Different timeslot
        )

        conflicts = detector.find_professor_conflicts([course_a, course_b])

        assert conflicts == []

    def test_conflict_when_same_professor_teaches_at_same_timeslot(
        self,
        detector: ConflictDetector,
        professor_alice: Professor,
        classroom_101: Classroom,
        classroom_202: Classroom,
        monday_period_1: TimeSlot,
    ) -> None:
        """GIVEN Alice is assigned to two courses at the SAME timeslot
        WHEN we check for professor conflicts
        THEN a conflict should be detected
        """
        course_a = Course.from_timeslot(
            id="course-001",
            name="Machine Learning",
            professor_id=professor_alice.id,
            classroom_id=classroom_101.id,
            timeslot=monday_period_1,
        )
        course_b = Course.from_timeslot(
            id="course-002",
            name="Deep Learning",
            professor_id=professor_alice.id,
            classroom_id=classroom_202.id,
            timeslot=monday_period_1,  # SAME timeslot - CONFLICT!
        )

        conflicts = detector.find_professor_conflicts([course_a, course_b])

        assert len(conflicts) == 1
        assert (course_a, course_b) in conflicts or (course_b, course_a) in conflicts

    def test_no_conflict_when_different_professors_at_same_timeslot(
        self,
        detector: ConflictDetector,
        professor_alice: Professor,
        professor_bob: Professor,
        classroom_101: Classroom,
        classroom_202: Classroom,
        monday_period_1: TimeSlot,
    ) -> None:
        """GIVEN Alice and Bob teach at the same timeslot (different rooms)
        WHEN we check for professor conflicts
        THEN no conflicts should be found
        """
        course_a = Course.from_timeslot(
            id="course-001",
            name="Machine Learning",
            professor_id=professor_alice.id,
            classroom_id=classroom_101.id,
            timeslot=monday_period_1,
        )
        course_b = Course.from_timeslot(
            id="course-002",
            name="Database Systems",
            professor_id=professor_bob.id,  # Different professor
            classroom_id=classroom_202.id,
            timeslot=monday_period_1,
        )

        conflicts = detector.find_professor_conflicts([course_a, course_b])

        assert conflicts == []


class TestClassroomConflict:
    """Test suite: A Classroom cannot host two courses at the same TimeSlot."""

    @pytest.fixture
    def detector(self) -> ConflictDetector:
        return ConflictDetector()

    def test_no_conflict_when_classroom_used_at_different_timeslots(
        self,
        detector: ConflictDetector,
        professor_alice: Professor,
        professor_bob: Professor,
        classroom_101: Classroom,
        monday_period_1: TimeSlot,
        monday_period_2: TimeSlot,
    ) -> None:
        """GIVEN Room 101 is used for two courses at different timeslots
        WHEN we check for classroom conflicts
        THEN no conflicts should be found
        """
        course_a = Course.from_timeslot(
            id="course-001",
            name="Machine Learning",
            professor_id=professor_alice.id,
            classroom_id=classroom_101.id,
            timeslot=monday_period_1,
        )
        course_b = Course.from_timeslot(
            id="course-002",
            name="Database Systems",
            professor_id=professor_bob.id,
            classroom_id=classroom_101.id,  # Same room
            timeslot=monday_period_2,  # Different timeslot
        )

        conflicts = detector.find_classroom_conflicts([course_a, course_b])

        assert conflicts == []

    def test_conflict_when_same_classroom_used_at_same_timeslot(
        self,
        detector: ConflictDetector,
        professor_alice: Professor,
        professor_bob: Professor,
        classroom_101: Classroom,
        monday_period_1: TimeSlot,
    ) -> None:
        """GIVEN Room 101 is booked for two courses at the SAME timeslot
        WHEN we check for classroom conflicts
        THEN a conflict should be detected
        """
        course_a = Course.from_timeslot(
            id="course-001",
            name="Machine Learning",
            professor_id=professor_alice.id,
            classroom_id=classroom_101.id,
            timeslot=monday_period_1,
        )
        course_b = Course.from_timeslot(
            id="course-002",
            name="Database Systems",
            professor_id=professor_bob.id,
            classroom_id=classroom_101.id,  # SAME room
            timeslot=monday_period_1,  # SAME timeslot - CONFLICT!
        )

        conflicts = detector.find_classroom_conflicts([course_a, course_b])

        assert len(conflicts) == 1
        assert (course_a, course_b) in conflicts or (course_b, course_a) in conflicts

    def test_no_conflict_when_different_classrooms_at_same_timeslot(
        self,
        detector: ConflictDetector,
        professor_alice: Professor,
        professor_bob: Professor,
        classroom_101: Classroom,
        classroom_202: Classroom,
        monday_period_1: TimeSlot,
    ) -> None:
        """GIVEN two courses are in different rooms at the same timeslot
        WHEN we check for classroom conflicts
        THEN no conflicts should be found
        """
        course_a = Course.from_timeslot(
            id="course-001",
            name="Machine Learning",
            professor_id=professor_alice.id,
            classroom_id=classroom_101.id,
            timeslot=monday_period_1,
        )
        course_b = Course.from_timeslot(
            id="course-002",
            name="Database Systems",
            professor_id=professor_bob.id,
            classroom_id=classroom_202.id,  # Different room
            timeslot=monday_period_1,
        )

        conflicts = detector.find_classroom_conflicts([course_a, course_b])

        assert conflicts == []

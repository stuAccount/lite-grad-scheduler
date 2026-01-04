"""TDD tests for ScheduleGenerator - Automated schedule generation.

Business Rule:
Generate conflict-free course schedules automatically using constraint satisfaction.
"""

import pytest

from scheduler.domain.models import Classroom, Professor, TimeSlot, Weekday
from scheduler.services.conflict_detector import ConflictDetector
from scheduler.services.schedule_generator import ScheduleGenerator


class TestScheduleGenerator:
    """Test suite: Automated schedule generation."""

    @pytest.fixture
    def generator(self) -> ScheduleGenerator:
        return ScheduleGenerator()

    @pytest.fixture
    def detector(self) -> ConflictDetector:
        return ConflictDetector()

    @pytest.fixture
    def available_timeslots(self) -> list[TimeSlot]:
        """Available timeslots: Mon-Wed, periods 1-2."""
        return [
            TimeSlot(weekday=Weekday.MONDAY, period=1),
            TimeSlot(weekday=Weekday.MONDAY, period=2),
            TimeSlot(weekday=Weekday.TUESDAY, period=1),
            TimeSlot(weekday=Weekday.TUESDAY, period=2),
            TimeSlot(weekday=Weekday.WEDNESDAY, period=1),
            TimeSlot(weekday=Weekday.WEDNESDAY, period=2),
        ]

    def test_generate_schedule_for_single_course(
        self,
        generator: ScheduleGenerator,
        professor_alice: Professor,
        classroom_101: Classroom,
        available_timeslots: list[TimeSlot],
    ) -> None:
        """GIVEN one course request
        WHEN we generate a schedule
        THEN one course should be scheduled with a timeslot
        """
        course_requests = [
            {
                "id": "cs501",
                "name": "Machine Learning",
                "professor_id": professor_alice.id,
                "classroom_id": classroom_101.id,
            }
        ]

        courses = generator.generate_schedule(
            course_requests=course_requests,
            professors=[professor_alice],
            classrooms=[classroom_101],
            available_timeslots=available_timeslots,
        )

        assert len(courses) == 1
        assert courses[0].id == "cs501"
        assert courses[0].professor_id == professor_alice.id
        assert courses[0].classroom_id == classroom_101.id
        # Timeslot should be one of the available ones
        assert courses[0].timeslot in available_timeslots

    def test_generated_schedule_has_no_conflicts(
        self,
        generator: ScheduleGenerator,
        detector: ConflictDetector,
        professor_alice: Professor,
        professor_bob: Professor,
        classroom_101: Classroom,
        classroom_202: Classroom,
        available_timeslots: list[TimeSlot],
    ) -> None:
        """GIVEN multiple course requests
        WHEN we generate a schedule
        THEN the generated schedule must be conflict-free
        """
        course_requests = [
            {
                "id": "cs501",
                "name": "Machine Learning",
                "professor_id": professor_alice.id,
                "classroom_id": classroom_101.id,
            },
            {
                "id": "cs502",
                "name": "Deep Learning",
                "professor_id": professor_alice.id,
                "classroom_id": classroom_202.id,
            },
            {
                "id": "cs601",
                "name": "Database Systems",
                "professor_id": professor_bob.id,
                "classroom_id": classroom_101.id,
            },
        ]

        courses = generator.generate_schedule(
            course_requests=course_requests,
            professors=[professor_alice, professor_bob],
            classrooms=[classroom_101, classroom_202],
            available_timeslots=available_timeslots,
        )

        # Verify no professor conflicts
        prof_conflicts = detector.find_professor_conflicts(courses)
        assert prof_conflicts == []

        # Verify no classroom conflicts
        room_conflicts = detector.find_classroom_conflicts(courses)
        assert room_conflicts == []

    def test_impossible_schedule_raises_error(
        self,
        generator: ScheduleGenerator,
        professor_alice: Professor,
        classroom_101: Classroom,
    ) -> None:
        """GIVEN more courses than available timeslots
        WHEN we generate a schedule
        THEN ValueError should be raised
        """
        # Only 1 timeslot but 2 courses with same professor
        limited_timeslots = [TimeSlot(weekday=Weekday.MONDAY, period=1)]

        course_requests = [
            {
                "id": "cs501",
                "name": "Machine Learning",
                "professor_id": professor_alice.id,
                "classroom_id": classroom_101.id,
            },
            {
                "id": "cs502",
                "name": "Deep Learning",
                "professor_id": professor_alice.id,
                "classroom_id": classroom_101.id,
            },
        ]

        with pytest.raises(ValueError, match="No valid schedule found"):
            generator.generate_schedule(
                course_requests=course_requests,
                professors=[professor_alice],
                classrooms=[classroom_101],
                available_timeslots=limited_timeslots,
            )

    def test_schedule_respects_different_professors_same_time(
        self,
        generator: ScheduleGenerator,
        professor_alice: Professor,
        professor_bob: Professor,
        classroom_101: Classroom,
        classroom_202: Classroom,
        available_timeslots: list[TimeSlot],
    ) -> None:
        """GIVEN two courses with different professors and classrooms
        WHEN we generate a schedule
        THEN they CAN be scheduled at the same timeslot
        """
        course_requests = [
            {
                "id": "cs501",
                "name": "Machine Learning",
                "professor_id": professor_alice.id,
                "classroom_id": classroom_101.id,
            },
            {
                "id": "cs601",
                "name": "Database Systems",
                "professor_id": professor_bob.id,
                "classroom_id": classroom_202.id,
            },
        ]

        courses = generator.generate_schedule(
            course_requests=course_requests,
            professors=[professor_alice, professor_bob],
            classrooms=[classroom_101, classroom_202],
            available_timeslots=available_timeslots,
        )

        # Should successfully generate (doesn't throw error)
        assert len(courses) == 2
        # Courses can potentially share a timeslot (no conflict since different prof+room)

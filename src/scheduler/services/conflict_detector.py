"""Conflict detection service for scheduling constraints."""

from collections.abc import Callable

from scheduler.domain.models import Course


class ConflictDetector:
    """Detects scheduling conflicts (hard constraints).

    Hard constraints:
    - A professor cannot teach two courses at the same timeslot.
    - A classroom cannot host two courses at the same timeslot.
    """

    def find_professor_conflicts(
        self, courses: list[Course]
    ) -> list[tuple[Course, Course]]:
        """Find courses where the same professor is double-booked.

        Args:
            courses: List of scheduled courses to check.

        Returns:
            List of conflicting course pairs.
        """
        return self._find_conflicts(
            courses,
            lambda a, b: a.professor_id == b.professor_id
        )

    def find_classroom_conflicts(
        self, courses: list[Course]
    ) -> list[tuple[Course, Course]]:
        """Find courses where the same classroom is double-booked.

        Args:
            courses: List of scheduled courses to check.

        Returns:
            List of conflicting course pairs.
        """
        return self._find_conflicts(
            courses,
            lambda a, b: a.classroom_id == b.classroom_id
        )

    def _find_conflicts(
        self,
        courses: list[Course],
        resource_matcher: Callable[[Course, Course], bool]
    ) -> list[tuple[Course, Course]]:
        """Generic conflict finder for same timeslot + same resource.

        Args:
            courses: List of courses to check.
            resource_matcher: Function to check if two courses use the same resource.

        Returns:
            List of conflicting course pairs.
        """
        conflicts = []
        for i in range(len(courses)):
            for j in range(i + 1, len(courses)):
                course_a, course_b = courses[i], courses[j]
                if (resource_matcher(course_a, course_b)
                    and course_a.timeslot == course_b.timeslot):
                    conflicts.append((course_a, course_b))
        return conflicts

"""Automated schedule generation using constraint satisfaction."""

from ortools.sat.python import cp_model

from scheduler.domain.models import Classroom, Course, Professor, TimeSlot


class ScheduleGenerator:
    """Generates conflict-free course schedules using OR-Tools CP-SAT solver.

    Uses constraint programming to assign timeslots to courses while ensuring:
    - No professor is double-booked (hard constraint)
    - No classroom is double-booked (hard constraint)
    """

    def generate_schedule(
        self,
        course_requests: list[dict],
        professors: list[Professor],
        classrooms: list[Classroom],
        available_timeslots: list[TimeSlot],
    ) -> list[Course]:
        """Generate a conflict-free schedule.

        Args:
            course_requests: List of courses to schedule. Each dict contains:
                - id: str
                - name: str
                - professor_id: str
                - classroom_id: str
            professors: Available professors.
            classrooms: Available classrooms.
            available_timeslots: Available time slots to assign.

        Returns:
            List of Course objects with assigned timeslots.

        Raises:
            ValueError: If no valid schedule can be found.
        """
        if not course_requests:
            return []

        model = cp_model.CpModel()

        # Create variables: each course gets assigned a timeslot index
        course_timeslot_vars = {}
        for course in course_requests:
            course_timeslot_vars[course["id"]] = model.NewIntVar(
                0, len(available_timeslots) - 1, f"timeslot_{course['id']}"
            )

        # Hard Constraint 1: No professor double-booking
        # Group courses by professor
        prof_courses = {}
        for course in course_requests:
            prof_id = course["professor_id"]
            if prof_id not in prof_courses:
                prof_courses[prof_id] = []
            prof_courses[prof_id].append(course["id"])

        # For each professor, all their courses must have different timeslots
        for prof_id, course_ids in prof_courses.items():
            if len(course_ids) > 1:
                model.AddAllDifferent(
                    [course_timeslot_vars[cid] for cid in course_ids]
                )

        # Hard Constraint 2: No classroom double-booking
        # Group courses by classroom
        room_courses = {}
        for course in course_requests:
            room_id = course["classroom_id"]
            if room_id not in room_courses:
                room_courses[room_id] = []
            room_courses[room_id].append(course["id"])

        # For each classroom, all courses must have different timeslots
        for room_id, course_ids in room_courses.items():
            if len(course_ids) > 1:
                model.AddAllDifferent(
                    [course_timeslot_vars[cid] for cid in course_ids]
                )

        # Solve the constraint satisfaction problem
        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            # Build Course objects with assigned timeslots
            scheduled_courses = []
            for course_req in course_requests:
                timeslot_idx = solver.Value(course_timeslot_vars[course_req["id"]])
                assigned_timeslot = available_timeslots[timeslot_idx]

                course = Course.from_timeslot(
                    id=course_req["id"],
                    name=course_req["name"],
                    professor_id=course_req["professor_id"],
                    classroom_id=course_req["classroom_id"],
                    timeslot=assigned_timeslot,
                )
                scheduled_courses.append(course)

            return scheduled_courses
        else:
            raise ValueError("No valid schedule found - constraints cannot be satisfied")

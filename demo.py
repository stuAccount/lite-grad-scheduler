"""Demo script showcasing conflict detection with mock data.

Run with: uv run python demo.py
"""

from scheduler.domain.models import Classroom, Course, Professor, TimeSlot, Weekday
from scheduler.services.conflict_detector import ConflictDetector


def main() -> None:
    """Demonstrate conflict detection on a mock course schedule."""
    # Create mock data
    prof_alice = Professor(id="prof-001", name="Alice Wang")
    prof_bob = Professor(id="prof-002", name="Bob Chen")
    prof_carol = Professor(id="prof-003", name="Carol Li")

    room_101 = Classroom(id="room-101", name="Building A Room 101", capacity=50)
    room_202 = Classroom(id="room-202", name="Building B Room 202", capacity=100)

    monday_1 = TimeSlot(weekday=Weekday.MONDAY, period=1)
    monday_2 = TimeSlot(weekday=Weekday.MONDAY, period=2)
    tuesday_1 = TimeSlot(weekday=Weekday.TUESDAY, period=1)

    # Create course schedule
    courses = [
        Course(
            id="cs501",
            name="Machine Learning",
            professor=prof_alice,
            classroom=room_101,
            timeslot=monday_1,
        ),
        Course(
            id="cs502",
            name="Deep Learning",
            professor=prof_alice,  # CONFLICT: Alice double-booked!
            classroom=room_202,
            timeslot=monday_1,
        ),
        Course(
            id="cs601",
            name="Database Systems",
            professor=prof_bob,
            classroom=room_101,  # CONFLICT: Room 101 double-booked!
            timeslot=monday_1,
        ),
        Course(
            id="cs701",
            name="Distributed Systems",
            professor=prof_carol,
            classroom=room_202,
            timeslot=monday_2,  # No conflict - different timeslot
        ),
        Course(
            id="cs801",
            name="Natural Language Processing",
            professor=prof_alice,
            classroom=room_101,
            timeslot=tuesday_1,  # No conflict - different day
        ),
    ]

    # Check for conflicts
    detector = ConflictDetector()

    print("🎓 Graduate Course Scheduling Demo")
    print("=" * 70)
    print()

    # Display schedule
    print("📅 Current Schedule:")
    for course in courses:
        print(
            f"  • {course.name} ({course.id})\n"
            f"    Professor: {course.professor.name}\n"
            f"    Room: {course.classroom.name}\n"
            f"    Time: {course.timeslot.weekday.name} Period {course.timeslot.period}\n"
        )

    print()
    print("🔍 Conflict Detection Results:")
    print("-" * 70)

    # Professor conflicts
    prof_conflicts = detector.find_professor_conflicts(courses)
    if prof_conflicts:
        print(f"\n⚠️  PROFESSOR CONFLICTS FOUND: {len(prof_conflicts)}")
        for c1, c2 in prof_conflicts:
            print(
                f"  • {c1.professor.name} is double-booked:\n"
                f"    - {c1.name} ({c1.timeslot.weekday.name} P{c1.timeslot.period})\n"
                f"    - {c2.name} ({c2.timeslot.weekday.name} P{c2.timeslot.period})"
            )
    else:
        print("\n✅ No professor conflicts")

    # Classroom conflicts
    room_conflicts = detector.find_classroom_conflicts(courses)
    if room_conflicts:
        print(f"\n⚠️  CLASSROOM CONFLICTS FOUND: {len(room_conflicts)}")
        for c1, c2 in room_conflicts:
            print(
                f"  • {c1.classroom.name} is double-booked:\n"
                f"    - {c1.name} ({c1.timeslot.weekday.name} P{c1.timeslot.period})\n"
                f"    - {c2.name} ({c2.timeslot.weekday.name} P{c2.timeslot.period})"
            )
    else:
        print("\n✅ No classroom conflicts")

    print()
    print("=" * 70)
    print("✨ Demo complete!")


if __name__ == "__main__":
    main()

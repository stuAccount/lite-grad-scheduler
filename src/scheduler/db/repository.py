"""Repository pattern for data access."""

from sqlmodel import Session, select

from scheduler.domain.models import Classroom, Course, Professor


class CourseRepository:
    """Repository for course-related database operations."""

    def __init__(self, session: Session):
        self.session = session

    def add_professor(self, professor: Professor) -> Professor:
        """Add a professor to the database.

        Args:
            professor: Professor entity to add.

        Returns:
            The added professor with any database-generated fields.
        """
        self.session.add(professor)
        self.session.commit()
        self.session.refresh(professor)
        return professor

    def add_classroom(self, classroom: Classroom) -> Classroom:
        """Add a classroom to the database.

        Args:
            classroom: Classroom entity to add.

        Returns:
            The added classroom.
        """
        self.session.add(classroom)
        self.session.commit()
        self.session.refresh(classroom)
        return classroom

    def add_course(self, course: Course) -> Course:
        """Add a course to the database.

        Args:
            course: Course entity to add.

        Returns:
            The added course.
        """
        self.session.add(course)
        self.session.commit()
        self.session.refresh(course)
        return course

    def get_all_courses(self) -> list[Course]:
        """Retrieve all courses from the database.

        Returns:
            List of all courses.
        """
        statement = select(Course)
        return list(self.session.exec(statement).all())

    def get_all_professors(self) -> list[Professor]:
        """Retrieve all professors."""
        statement = select(Professor)
        return list(self.session.exec(statement).all())

    def get_all_classrooms(self) -> list[Classroom]:
        """Retrieve all classrooms."""
        statement = select(Classroom)
        return list(self.session.exec(statement).all())

    def get_professor_by_id(self, professor_id: str) -> Professor | None:
        """Get a professor by ID.

        Args:
            professor_id: The professor's ID.

        Returns:
            The professor if found, None otherwise.
        """
        statement = select(Professor).where(Professor.id == professor_id)
        return self.session.exec(statement).first()

    def get_classroom_by_id(self, classroom_id: str) -> Classroom | None:
        """Get a classroom by ID.

        Args:
            classroom_id: The classroom's ID.

        Returns:
            The classroom if found, None otherwise.
        """
        statement = select(Classroom).where(Classroom.id == classroom_id)
        return self.session.exec(statement).first()

    def get_courses_by_professor(self, professor_id: str) -> list[Course]:
        """Get all courses taught by a specific professor.

        Args:
            professor_id: The professor's ID.

        Returns:
            List of courses taught by the professor.
        """
        statement = select(Course).where(Course.professor_id == professor_id)
        return list(self.session.exec(statement).all())

    def get_courses_by_classroom(self, classroom_id: str) -> list[Course]:
        """Get all courses held in a specific classroom.

        Args:
            classroom_id: The classroom's ID.

        Returns:
            List of courses held in the classroom.
        """
        statement = select(Course).where(Course.classroom_id == classroom_id)
        return list(self.session.exec(statement).all())

    def get_all_courses_ordered(self) -> list[Course]:
        """Get all courses ordered by weekday and period.

        Returns:
            List of all courses sorted by schedule.
        """
        statement = select(Course).order_by(Course.weekday, Course.period)
        return list(self.session.exec(statement).all())



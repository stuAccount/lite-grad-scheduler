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


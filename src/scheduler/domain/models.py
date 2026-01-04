"""Core domain models for graduate course scheduling."""

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    pass


class Weekday(Enum):
    """Days of the week for scheduling."""

    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5


class CourseType(Enum):
    """Course types for graduate programs."""

    REQUIRED = "required"  # 必修 (Required)
    ELECTIVE = "elective"  # 选修 (Elective)


class ProfessorTitle(Enum):
    """Academic titles for professors."""

    ASSISTANT = "assistant"  # 助教
    LECTURER = "lecturer"    # 讲师
    ASSOCIATE = "associate"  # 副教授
    FULL = "full"            # 教授


@dataclass(frozen=True)
class TimeSlot:
    """Value Object: Immutable time window for scheduling.

    Attributes:
        weekday: The day of the week.
        period: Class period number (1-12).
    """

    weekday: Weekday
    period: int  # 1-12 representing class periods

    def __post_init__(self) -> None:
        if not 1 <= self.period <= 12:
            raise ValueError(f"Period must be between 1 and 12, got {self.period}")


class Professor(SQLModel, table=True):
    """Entity: A professor who teaches courses."""

    id: str = Field(primary_key=True)
    name: str

    # Academic metadata (optional)
    department: str | None = Field(default=None)  # 系部
    title: str | None = Field(default=None)       # 职称 (store enum value)

    # Relationship
    courses: list["Course"] = Relationship(back_populates="professor")


class Classroom(SQLModel, table=True):
    """Entity: A physical room where courses are held."""

    id: str = Field(primary_key=True)
    name: str
    capacity: int

    # Relationship
    courses: list["Course"] = Relationship(back_populates="classroom")


class Course(SQLModel, table=True):
    """Entity: A scheduled course linking professor, classroom, and timeslot."""

    id: str = Field(primary_key=True)
    name: str

    # Foreign keys
    professor_id: str = Field(foreign_key="professor.id")
    classroom_id: str = Field(foreign_key="classroom.id")

    # TimeSlot flattened into columns
    weekday: int  # Store Weekday.value (1-5)
    period: int  # 1-12

    # Academic metadata (optional)
    credits: float | None = Field(default=None)      # 学分
    hours: int | None = Field(default=None)          # 学时
    course_type: str | None = Field(default=None)    # 必修/选修 (store enum value)
    department: str | None = Field(default=None)     # 开课学院

    # Relationships
    professor: Professor = Relationship(back_populates="courses")
    classroom: Classroom = Relationship(back_populates="courses")

    @property
    def timeslot(self) -> TimeSlot:
        """Reconstruct TimeSlot value object from database columns."""
        return TimeSlot(weekday=Weekday(self.weekday), period=self.period)

    @classmethod
    def from_timeslot(
        cls,
        id: str,
        name: str,
        professor_id: str,
        classroom_id: str,
        timeslot: TimeSlot,
        credits: float | None = None,
        hours: int | None = None,
        course_type: str | None = None,
        department: str | None = None,
    ) -> "Course":
        """Create a Course from a TimeSlot value object."""
        return cls(
            id=id,
            name=name,
            professor_id=professor_id,
            classroom_id=classroom_id,
            weekday=timeslot.weekday.value,
            period=timeslot.period,
            credits=credits,
            hours=hours,
            course_type=course_type,
            department=department,
        )

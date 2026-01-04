"""Domain models for the scheduling system."""

from .models import (
    Weekday,
    TimeSlot,
    Professor,
    Classroom,
    Course,
    CourseType,
    ProfessorTitle,
)

__all__ = [
    "Weekday",
    "TimeSlot",
    "Professor",
    "Classroom",
    "Course",
    "CourseType",
    "ProfessorTitle",
]

"""Core domain models for graduate course scheduling."""

from dataclasses import dataclass
from enum import Enum


class Weekday(Enum):
    """Days of the week for scheduling."""

    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5


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


@dataclass
class Professor:
    """Entity: A professor who teaches courses."""

    id: str
    name: str


@dataclass
class Classroom:
    """Entity: A physical room where courses are held."""

    id: str
    name: str
    capacity: int


@dataclass
class Course:
    """Entity: A scheduled course linking professor, classroom, and timeslot."""

    id: str
    name: str
    professor: Professor
    classroom: Classroom
    timeslot: TimeSlot

"""Pytest fixtures with mock/seeded data for testing."""

import pytest

from scheduler.domain.models import Classroom, Professor, TimeSlot, Weekday


# ============================================================================
# Professor Fixtures
# ============================================================================


@pytest.fixture
def professor_alice() -> Professor:
    """Professor Alice Wang - teaches Machine Learning."""
    return Professor(id="prof-001", name="Alice Wang")


@pytest.fixture
def professor_bob() -> Professor:
    """Professor Bob Chen - teaches Database Systems."""
    return Professor(id="prof-002", name="Bob Chen")


# ============================================================================
# Classroom Fixtures
# ============================================================================


@pytest.fixture
def classroom_101() -> Classroom:
    """Room 101 - Medium lecture hall."""
    return Classroom(id="room-101", name="Room 101", capacity=50)


@pytest.fixture
def classroom_202() -> Classroom:
    """Room 202 - Large lecture hall."""
    return Classroom(id="room-202", name="Room 202", capacity=100)


# ============================================================================
# TimeSlot Fixtures
# ============================================================================


@pytest.fixture
def monday_period_1() -> TimeSlot:
    """Monday, first period (morning)."""
    return TimeSlot(weekday=Weekday.MONDAY, period=1)


@pytest.fixture
def monday_period_2() -> TimeSlot:
    """Monday, second period."""
    return TimeSlot(weekday=Weekday.MONDAY, period=2)


@pytest.fixture
def tuesday_period_1() -> TimeSlot:
    """Tuesday, first period (morning)."""
    return TimeSlot(weekday=Weekday.TUESDAY, period=1)

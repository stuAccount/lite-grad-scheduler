"""Course management API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from scheduler.db import get_session
from scheduler.db.repository import CourseRepository
from scheduler.domain.models import Classroom, Course, Professor, TimeSlot, Weekday
from scheduler.services.conflict_detector import ConflictDetector
from scheduler.services.schedule_generator import ScheduleGenerator

router = APIRouter(prefix="/courses", tags=["courses"])


# Request/Res schemas
class TimeSlotSchema(BaseModel):
    """TimeSlot for API requests."""

    weekday: int  # 1-5
    period: int  # 1-12


class CourseCreateRequest(BaseModel):
    """Request schema for creating a course."""

    id: str
    name: str
    professor_id: str
    classroom_id: str
    timeslot: TimeSlotSchema


class CourseRequestSchema(BaseModel):
    """Schema for a course to be scheduled (no timeslot yet)."""

    id: str
    name: str
    professor_id: str
    classroom_id: str


class ScheduleGenerateRequest(BaseModel):
    """Request schema for automated scheduling."""

    course_requests: list[CourseRequestSchema]


class ProfessorCreateRequest(BaseModel):
    """Request schema for creating a professor."""

    id: str
    name: str


class ClassroomCreateRequest(BaseModel):
    """Request schema for creating a classroom."""

    id: str
    name: str
    capacity: int


class ConflictResponse(BaseModel):
    """Response schema for conflict detection."""

    professor_conflicts: int
    classroom_conflicts: int
    details: dict


@router.post("/professors", status_code=201)
def create_professor(
    professor_data: ProfessorCreateRequest, session: Session = Depends(get_session)
):
    """Create a new professor."""
    repo = CourseRepository(session)
    professor = Professor(**professor_data.model_dump())
    return repo.add_professor(professor)


@router.post("/classrooms", status_code=201)
def create_classroom(
    classroom_data: ClassroomCreateRequest, session: Session = Depends(get_session)
):
    """Create a new classroom."""
    repo = CourseRepository(session)
    classroom = Classroom(**classroom_data.model_dump())
    return repo.add_classroom(classroom)


@router.post("/", status_code=201)
def create_course(
    course_data: CourseCreateRequest, session: Session = Depends(get_session)
):
    """Create a new course.
    
    Args:
        course_data: Course creation data.
        session: Database session.
    
    Returns:
        The created course.
    
    Raises:
        HTTPException: If the timeslot data is invalid.
    """
    repo = CourseRepository(session)
    
    # Validate and create TimeSlot
    try:
        timeslot = TimeSlot(
            weekday=Weekday(course_data.timeslot.weekday),
            period=course_data.timeslot.period
        )
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid timeslot: {e}")
    
    # Create Course using from_timeslot
    course = Course.from_timeslot(
        id=course_data.id,
        name=course_data.name,
        professor_id=course_data.professor_id,
        classroom_id=course_data.classroom_id,
        timeslot=timeslot,
    )
    
    return repo.add_course(course)


@router.get("/")
def list_courses(session: Session = Depends(get_session)):
    """List all courses."""
    repo = CourseRepository(session)
    return repo.get_all_courses()


@router.post("/check-conflicts")
def check_conflicts(session: Session = Depends(get_session)) -> ConflictResponse:
    """Check for scheduling conflicts among all courses.
    
    Returns:
        Conflict detection results with counts and details.
    """
    repo = CourseRepository(session)
    courses = repo.get_all_courses()
    detector = ConflictDetector()
    
    prof_conflicts = detector.find_professor_conflicts(courses)
    room_conflicts = detector.find_classroom_conflicts(courses)
    
    # Build details
    prof_details = [
        {
            "course_a": {"id": c1.id, "name": c1.name},
            "course_b": {"id": c2.id, "name": c2.name},
            "professor_id": c1.professor_id,
            "timeslot": {"weekday": c1.weekday, "period": c1.period}
        }
        for c1, c2 in prof_conflicts
    ]
    
    room_details = [
        {
            "course_a": {"id": c1.id, "name": c1.name},
            "course_b": {"id": c2.id, "name": c2.name},
            "classroom_id": c1.classroom_id,
            "timeslot": {"weekday": c1.weekday, "period": c1.period}
        }
        for c1, c2 in room_conflicts
    ]
    
    return ConflictResponse(
        professor_conflicts=len(prof_conflicts),
        classroom_conflicts=len(room_conflicts),
        details={
            "professor_conflicts": prof_details,
            "classroom_conflicts": room_details,
        }
    )


@router.post("/schedules/generate")
def generate_schedule(
    request: ScheduleGenerateRequest, session: Session = Depends(get_session)
):
    """Generate a conflict-free schedule automatically.

    Args:
        request: Schedule generation request with course list.
        session: Database session.

    Returns:
        Generated schedule with courses assigned to timeslots.

    Raises:
        HTTPException: If schedule cannot be generated or resources not found.
    """
    repo = CourseRepository(session)
    
    # Get all professors and classrooms from database
    professors = repo.get_all_professors()
    classrooms = repo.get_all_classrooms()
    
    # Define available timeslots (Mon-Fri, periods 1-8)
    available_timeslots = [
        TimeSlot(weekday=Weekday(day), period=period)
        for day in range(1, 6)  # Mon-Fri
        for period in range(1, 9)  # Periods 1-8
    ]
    
    # Convert Pydantic models to dicts for ScheduleGenerator
    course_requests_dicts = [
        {
            "id": cr.id,
            "name": cr.name,
            "professor_id": cr.professor_id,
            "classroom_id": cr.classroom_id,
        }
        for cr in request.course_requests
    ]
    
    # Generate schedule
    generator = ScheduleGenerator()
    try:
        courses = generator.generate_schedule(
            course_requests=course_requests_dicts,
            professors=professors,
            classrooms=classrooms,
            available_timeslots=available_timeslots,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Optionally save generated courses to database
    saved_courses = []
    for course in courses:
        saved_course = repo.add_course(course)
        # Convert SQLModel to dict for JSON response
        saved_courses.append(saved_course.model_dump(mode="json"))
    
    return {
        "message": "Schedule generated successfully",
        "courses": saved_courses,
        "total": len(saved_courses),
    }

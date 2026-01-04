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

    # Academic metadata (optional)
    credits: float | None = None
    hours: int | None = None
    course_type: str | None = None  # CourseType enum value
    department: str | None = None


class CourseRequestSchema(BaseModel):
    """Schema for a course to be scheduled (no timeslot yet)."""

    id: str
    name: str
    professor_id: str
    classroom_id: str

    # Academic metadata (optional)
    credits: float | None = None
    hours: int | None = None
    course_type: str | None = None
    department: str | None = None


class ScheduleGenerateRequest(BaseModel):
    """Request schema for automated scheduling."""

    course_requests: list[CourseRequestSchema]


class ProfessorCreateRequest(BaseModel):
    """Request schema for creating a professor."""

    id: str
    name: str

    # Academic metadata (optional)
    department: str | None = None
    title: str | None = None  # ProfessorTitle enum value


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


@router.get("/professors")
def list_professors(session: Session = Depends(get_session)):
    """List all professors."""
    repo = CourseRepository(session)
    return repo.get_all_professors()


@router.post("/classrooms", status_code=201)
def create_classroom(
    classroom_data: ClassroomCreateRequest, session: Session = Depends(get_session)
):
    """Create a new classroom."""
    repo = CourseRepository(session)
    classroom = Classroom(**classroom_data.model_dump())
    return repo.add_classroom(classroom)


@router.get("/classrooms")
def list_classrooms(session: Session = Depends(get_session)):
    """List all classrooms."""
    repo = CourseRepository(session)
    return repo.get_all_classrooms()


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
    
    # Validate professor exists
    professor = repo.get_professor_by_id(course_data.professor_id)
    if professor is None:
        raise HTTPException(
            status_code=404,
            detail=f"Professor not found: {course_data.professor_id}"
        )
    
    # Validate classroom exists
    classroom = repo.get_classroom_by_id(course_data.classroom_id)
    if classroom is None:
        raise HTTPException(
            status_code=404,
            detail=f"Classroom not found: {course_data.classroom_id}"
        )
    
    # Create Course using from_timeslot
    course = Course.from_timeslot(
        id=course_data.id,
        name=course_data.name,
        professor_id=course_data.professor_id,
        classroom_id=course_data.classroom_id,
        timeslot=timeslot,
        credits=course_data.credits,
        hours=course_data.hours,
        course_type=course_data.course_type,
        department=course_data.department,
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
    
    # Validate all referenced professor and classroom IDs exist
    professor_ids = {p.id for p in professors}
    classroom_ids = {c.id for c in classrooms}
    
    missing_professors = []
    missing_classrooms = []
    
    for course_req in request.course_requests:
        if course_req.professor_id not in professor_ids:
            missing_professors.append(course_req.professor_id)
        if course_req.classroom_id not in classroom_ids:
            missing_classrooms.append(course_req.classroom_id)
    
    # Remove duplicates
    missing_professors = list(set(missing_professors))
    missing_classrooms = list(set(missing_classrooms))
    
    if missing_professors or missing_classrooms:
        error_parts = []
        if missing_professors:
            error_parts.append(f"Professors not found: {', '.join(missing_professors)}")
        if missing_classrooms:
            error_parts.append(f"Classrooms not found: {', '.join(missing_classrooms)}")
        raise HTTPException(status_code=404, detail="; ".join(error_parts))
    
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
            "credits": cr.credits,
            "hours": cr.hours,
            "course_type": cr.course_type,
            "department": cr.department,
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

@router.get("/schedules/professor/{professor_id}")
def get_professor_schedule(
    professor_id: str,
    session: Session = Depends(get_session)
):
    """Get schedule for a specific professor.
    
    Returns all courses taught by the professor with timeslots.
    """
    repo = CourseRepository(session)
    
    # Validate professor exists
    professor = repo.get_professor_by_id(professor_id)
    if professor is None:
        raise HTTPException(
            status_code=404,
            detail=f"Professor not found: {professor_id}"
        )
    
    courses = repo.get_courses_by_professor(professor_id)
    
    return {
        "professor": {"id": professor.id, "name": professor.name},
        "courses": [c.model_dump(mode="json") for c in courses],
        "total": len(courses)
    }


@router.get("/schedules/classroom/{classroom_id}")
def get_classroom_schedule(
    classroom_id: str,
    session: Session = Depends(get_session)
):
    """Get schedule for a specific classroom.
    
    Returns all courses held in the classroom with timeslots.
    """
    repo = CourseRepository(session)
    
    # Validate classroom exists
    classroom = repo.get_classroom_by_id(classroom_id)
    if classroom is None:
        raise HTTPException(
            status_code=404,
            detail=f"Classroom not found: {classroom_id}"
        )
    
    courses = repo.get_courses_by_classroom(classroom_id)
    
    return {
        "classroom": {"id": classroom.id, "name": classroom.name},
        "courses": [c.model_dump(mode="json") for c in courses],
        "total": len(courses)
    }


@router.get("/schedules/weekly")
def get_weekly_schedule(session: Session = Depends(get_session)):
    """Get full weekly schedule grid.
    
    Returns all courses organized by weekday and period.
    """
    repo = CourseRepository(session)
    courses = repo.get_all_courses_ordered()
    
    # Organize into grid structure
    grid = {}
    for day in range(1, 6):  # Mon-Fri
        grid[day] = {}
        for period in range(1, 13):  # Periods 1-12
            grid[day][period] = []
    
    for course in courses:
        if course.weekday and course.period:
            grid[course.weekday][course.period].append(course.model_dump(mode="json"))
    
    return {
        "grid": grid,
        "total_courses": len(courses)
    }

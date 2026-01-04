# lite-grad-scheduler 🎓

> "Wit beyond measure is man's greatest treasure."

A lightweight, logic-driven course scheduling system for graduate students built with **strict TDD methodology**.

---

## ✨ Features

### Release 1.0 (Implemented ✅)
- **Automated Scheduling**: OR-Tools powered conflict-free schedule generation
- **Hard Constraint Detection**: Professor and classroom double-booking prevention
- **REST API**: Full CRUD operations for professors, classrooms, and courses
- **SQLite Persistence**: Lightweight database with SQLModel ORM
- **Web Interface**: Modern UI for managing resources and generating schedules
- **Data Integrity Validation**: Referential integrity checks, dropdown selectors
- **Enhanced Metadata**: Course credits, hours, type; Professor department, title
- **Multi-View Schedules**: Query by professor, classroom, or weekly grid
- **Export Functionality**: PDF (formatted grid) and Excel (sortable data) exports
- **95% Test Coverage**: 35 passing tests (unit + integration)

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/stuAccount/lite-grad-scheduler.git
cd lite-grad-scheduler

# Install dependencies with uv
uv sync --all-extras
```

### Run the API Server

```bash
PYTHONPATH=src uv run uvicorn scheduler.api.main:app --reload
```

The API will be available at `http://localhost:8000`. Visit `http://localhost:8000/docs` for interactive API documentation.

---

## 📝 API Usage

### 1. Create a Professor

```bash
curl -X POST http://localhost:8000/courses/professors \
  -H "Content-Type: application/json" \
  -d '{"id": "prof-001", "name": "Alice Wang"}'
```

### 2. Create a Classroom

```bash
curl -X POST http://localhost:8000/courses/classrooms \
  -H "Content-Type: application/json" \
  -d '{"id": "room-101", "name": "Building A Room 101", "capacity": 50}'
```

### 3. Create a Course

```bash
curl -X POST http://localhost:8000/courses/ \
  -H "Content-Type: application/json" \
  -d '{
    "id": "cs501",
    "name": "Machine Learning",
    "professor_id": "prof-001",
    "classroom_id": "room-101",
    "timeslot": {"weekday": 1, "period": 1}
  }'
```

**TimeSlot Format:**
- `weekday`: 1 (Monday) to 5 (Friday)
- `period`: 1 to 12 (class period number)

### 4. Generate Automated Schedule

```bash
curl -X POST http://localhost:8000/courses/schedules/generate \
  -H "Content-Type: application/json" \
  -d '{
    "course_requests": [
      {"id": "cs501", "name": "ML", "professor_id": "prof-001", "classroom_id": "room-101"},
      {"id": "cs502", "name": "DL", "professor_id": "prof-001", "classroom_id": "room-102"}
    ]
  }'
```

### 5. Check for Conflicts

```bash
curl -X POST http://localhost:8000/courses/check-conflicts
```

---

## 🧪 Testing

```bash
# Run all tests
uv run pytest -v

# Run with coverage
uv run pytest --cov=scheduler --cov-report=term-missing

# Run only unit tests
uv run pytest tests/unit/ -v

# Run only integration tests
uv run pytest tests/integration/ -v
```

---

## 📁 Project Structure

```
lite-grad-scheduler/
├── src/scheduler/
│   ├── domain/          # Domain models (SQLModel tables)
│   ├── services/        # Business logic (ConflictDetector, ScheduleGenerator)
│   ├── db/              # Database layer (repository pattern)
│   └── api/             # FastAPI routes
├── static/              # Web UI (HTML/CSS/JS)
├── tests/
│   ├── unit/            # Fast, isolated tests
│   └── integration/     # API integration tests
├── demo.py              # Standalone demo script
└── pyproject.toml       # uv configuration
```

---

## 🎯 Constraint System

### Hard Constraints (Enforced)
1. **Professor Conflict**: A professor cannot teach two courses at the same timeslot
2. **Classroom Conflict**: A classroom cannot host two courses at the same timeslot

### Soft Constraints (Future)
- Professor time preferences
- Minimizing gaps between classes
- Room capacity matching

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.12 with type hints |
| API | FastAPI |
| ORM | SQLModel (SQLite) |
| Scheduler | Google OR-Tools CP-SAT |
| Testing | Pytest (94% coverage) |
| Package Manager | uv |

---

## 📊 Coverage

```
14 tests passing:
- 6 unit tests (conflict detection, schedule generation)
- 8 integration tests (API endpoints)
```

---

## 🚧 Roadmap

### ✅ Release 1.0 (Complete!)
- **Sprint 1** ✅: Conflict Detection MVP
- **Sprint 2** ✅: Persistence + REST API
- **Sprint 3** ✅: Automated scheduling with OR-Tools
- **Sprint 4** ✅: Web UI
- **Sprint 5** ✅: Data integrity validation
- **Sprint 6** ✅: Enhanced course/professor metadata
- **Sprint 7** ✅: Multi-view schedule queries
- **Sprint 8** ✅: PDF/Excel export

### 🔮 Future Releases
- Admin authentication & role-based access
- Student enrollment model
- Drag-and-drop schedule adjustment
- Mid-semester change management

---

## 📄 License

MIT License. This project follows XP (Extreme Programming) methodology with strict TDD.
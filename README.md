# lite-grad-scheduler 🎓

> "Wit beyond measure is man's greatest treasure."

A lightweight, logic-driven course scheduling system for graduate students built with **strict TDD methodology**.

---

## ✨ Features

- **Hard Constraint Detection**: Detects professor and classroom double-booking
- **REST API**: Full CRUD operations for professors, classrooms, and courses
- **SQLite Persistence**: Lightweight database with SQLModel ORM
- **98% Test Coverage**: Comprehensive unit and integration tests

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

### 4. List All Courses

```bash
curl http://localhost:8000/courses/
```

### 5. Check for Conflicts

```bash
curl -X POST http://localhost:8000/courses/check-conflicts
```

**Response:**
```json
{
  "professor_conflicts": 1,
  "classroom_conflicts": 0,
  "details": {
    "professor_conflicts": [
      {
        "course_a": {"id": "cs501", "name": "Machine Learning"},
        "course_b": {"id": "cs502", "name": "Deep Learning"},
        "professor_id": "prof-001",
        "timeslot": {"weekday": 1, "period": 1}
      }
    ],
    "classroom_conflicts": []
  }
}
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
│   ├── services/        # Business logic (ConflictDetector)
│   ├── db/              # Database layer (repository pattern)
│   └── api/             # FastAPI routes
├── tests/
│   ├── unit/            # Fast, isolated tests
│   └── integration/     # API integration tests
├── demo.py              # Standalone demo script
└── pyproject.toml       # uv configuration
```

---

## 🎯 Conflict Detection Rules

### Hard Constraints

1. **Professor Conflict**: A professor cannot teach two courses at the same timeslot
2. **Classroom Conflict**: A classroom cannot host two courses at the same timeslot

Both constraints are enforced via the `/courses/check-conflicts` endpoint.

---

## 🛠️ Tech Stack

- **Python 3.12** with type hints
- **FastAPI** for REST API
- **SQLModel** for ORM (SQLite)
- **Pytest** for testing
- **uv** for dependency management

---

## 📊 Test Coverage

**Current Coverage: 94%**

```
14 tests passing:
- 6 unit tests (conflict detection logic)
- 8 integration tests (API endpoints)
```

---

## 🚧 Roadmap

- **Sprint 1** ✅: Conflict Detection MVP
- **Sprint 2** ✅: Persistence + REST API
- **Sprint 3**: Advanced scheduling with OR-Tools
- **Sprint 4**: Web UI

---

## 📄 License

This project follows the XP (Extreme Programming) methodology with strict TDD.
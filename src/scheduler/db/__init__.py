"""Database session management and initialization."""

from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = "sqlite:///./scheduler.db"

# echo=False for production, echo=True for debugging SQL queries
engine = create_engine(DATABASE_URL, echo=False)


def init_db() -> None:
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency for database sessions.
    
    Yields:
        Session: SQLModel database session.
    """
    with Session(engine) as session:
        yield session

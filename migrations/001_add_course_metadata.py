"""Add academic metadata fields to Course and Professor models.

This migration adds the following columns:
- Course: credits, hours, course_type, department
- Professor: department, title

All columns are nullable for backward compatibility.
"""

from sqlmodel import create_engine, text

DATABASE_URL = "sqlite:///./scheduler.db"


def upgrade():
    """Add new columns to existing tables."""
    engine = create_engine(DATABASE_URL)
    
    with engine.begin() as conn:
        # Check if migration already ran by testing for one of the columns
        result = conn.execute(text("PRAGMA table_info(course)"))
        columns = [row[1] for row in result]
        
        if "credits" in columns:
            print("⏭️  Migration already applied, skipping...")
            return
        
        print("Running migration: 001_add_course_metadata")
        
        # Add Course metadata columns
        conn.execute(text("ALTER TABLE course ADD COLUMN credits REAL"))
        conn.execute(text("ALTER TABLE course ADD COLUMN hours INTEGER"))
        conn.execute(text("ALTER TABLE course ADD COLUMN course_type VARCHAR"))
        conn.execute(text("ALTER TABLE course ADD COLUMN department VARCHAR"))
        
        # Add Professor metadata columns  
        conn.execute(text("ALTER TABLE professor ADD COLUMN department VARCHAR"))
        conn.execute(text("ALTER TABLE professor ADD COLUMN title VARCHAR"))
        
    print("✅ Migration completed successfully")


def downgrade():
    """SQLite doesn't support DROP COLUMN easily."""
    print("⚠️  SQLite doesn't support DROP COLUMN.")
    print("    To rollback: restore from backup or recreate database.")


if __name__ == "__main__":
    upgrade()

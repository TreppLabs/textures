"""
Database configuration and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment
# If TESTING environment variable is set, force in-memory database
if os.getenv("TESTING") == "true":
    DATABASE_URL = "sqlite:///:memory:"
else:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/database/textures.db")

# Convert relative path to absolute path
if DATABASE_URL.startswith("sqlite:///./"):
    # Get the absolute path to the project root
    project_root = Path(__file__).parent.parent.parent.parent
    db_path = project_root / "data" / "database" / "textures.db"
    DATABASE_URL = f"sqlite:///{db_path}"

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base for models
Base = declarative_base()

def get_db():
    """
    Dependency to get database session.
    
    Yields:
        Database session that will be automatically closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Create all database tables.
    
    This should be called during application initialization.
    """
    Base.metadata.create_all(bind=engine)

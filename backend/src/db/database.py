import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.models import Base

# Strictly use SQLite for simplicity and easy deployment
# Use an absolute path for the SQLite file to ensure Render can always open it
# Check for a persistent mount path (e.g. Render Disk)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
db_path = os.getenv("DATABASE_PATH", os.path.join(BASE_DIR, "hireiq.db"))
DATABASE_URL = f"sqlite:///{db_path}"
print(f"--- DATABASE INITIALIZED AT: {db_path} ---")

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} # Required for SQLite + FastAPI
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initializes the local SQLite database."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.models import Base

# Strictly use SQLite for simplicity and easy deployment
# Use /data/hireiq.db if the persistent volume exists (Render), otherwise fallback to local
if os.path.exists("/data"):
    DATABASE_URL = "sqlite:////data/hireiq.db"
else:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hireiq.db")

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

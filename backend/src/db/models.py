from sqlalchemy import Column, String, Text, Integer, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class TaskRecord(Base):
    __tablename__ = "tasks"
    
    task_id = Column(String, primary_key=True, index=True)
    goal = Column(String, nullable=False)
    status = Column(String, default="running")
    current_node = Column(String, default="starting")
    percentage_complete = Column(Integer, default=0)
    retry_count = Column(Integer, default=0)
    report = Column(Text, nullable=True)
    execution_plan = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ScheduledTask(Base):
    __tablename__ = "scheduled_tasks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    goal = Column(String, nullable=False)
    interval_hours = Column(Integer, default=24)
    last_run = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from src.db.database import get_db, SessionLocal
from src.db.models import ScheduledTask, TaskRecord
from src.db.chroma import find_similar_goals
# We will import agent_graph inside the function to avoid circular imports if necessary
# or we can pass a function to trigger the agent

scheduler = AsyncIOScheduler()

async def check_scheduled_tasks():
    """
    Background job that runs periodically to check if any ScheduledTasks need to run.
    """
    db = SessionLocal()
    try:
        tasks = db.query(ScheduledTask).all()
        now = datetime.utcnow()
        for st in tasks:
            # Simple interval check (every N hours)
            if not st.last_run or (now - st.last_run).total_seconds() >= st.interval_hours * 3600:
                print(f"--- TRIGGERING PROACTIVE ALERT FOR: {st.goal} ---")
                
                # Check for significant drift using ChromaDB before running the full agent?
                # Actually, running the agent and then comparing the new report is more accurate.
                task_id = str(uuid.uuid4())
                new_task = TaskRecord(task_id=task_id, goal=st.goal)
                db.add(new_task)
                st.last_run = now
                db.commit()
                
                # We need to trigger run_agent_task from main.py.
                # To avoid circular imports, we can import it locally
                from src.api.main import run_agent_task
                
                # Ideally, this should run via BackgroundTasks, but since we are already
                # in a background thread/coroutine via APScheduler, we can just call it
                # synchronously or via asyncio.to_thread depending on how it's defined.
                import threading
                threading.Thread(target=run_agent_task, args=(task_id, st.goal)).start()
                
    except Exception as e:
        print(f"Error in scheduled tasks: {e}")
    finally:
        db.close()

def init_scheduler():
    scheduler.add_job(check_scheduled_tasks, 'interval', minutes=10) # Checks every 10 minutes
    scheduler.start()
    print("--- BACKGROUND SCHEDULER STARTED ---")

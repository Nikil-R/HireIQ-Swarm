from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
from sqlalchemy.orm import Session

# Import the LangGraph agent
from src.agent.graph import create_agent_graph
from src.db.database import init_db, get_db
from src.db.models import TaskRecord
from src.db.chroma import store_report_embedding, find_similar_goals

app = FastAPI(title="HireIQ API", description="Autonomous Recruitment Intelligence Agent")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the LangGraph application
agent_graph = create_agent_graph()

@app.on_event("startup")
def on_startup():
    init_db()

class ExecuteRequest(BaseModel):
    goal: str

def run_agent_task(task_id: str, goal: str):
    """
    Background task that executes the LangGraph agent and updates status continuously in SQLite.
    Also stores to ChromaDB when complete.
    """
    db = next(get_db())
    
    initial_state = {"raw_goal": goal}
    workflow_nodes = ["goal_parser", "planner", "executor", "verifier", "synthesizer", "report_generator"]
    
    try:
        # Use .stream() to get real-time state updates as the graph moves from node to node
        for output in agent_graph.stream(initial_state):
            for node_name, state_update in output.items():
                task = db.query(TaskRecord).filter(TaskRecord.task_id == task_id).first()
                if not task: continue
                
                task.current_node = node_name
                
                if node_name in workflow_nodes:
                    idx = workflow_nodes.index(node_name)
                    task.percentage_complete = int(((idx + 1) / len(workflow_nodes)) * 100)
                
                if "retry_count" in state_update:
                    task.retry_count = state_update["retry_count"]
                    
                if "execution_plan" in state_update:
                    import json
                    task.execution_plan = json.dumps(state_update["execution_plan"])
                    
                if node_name == "report_generator" and "final_report" in state_update:
                    task.report = state_update["final_report"]
                    
                db.commit()

        task = db.query(TaskRecord).filter(TaskRecord.task_id == task_id).first()
        if task:
            task.status = "completed"
            task.percentage_complete = 100
            db.commit()
            
            # Store in ChromaDB for future semantic search
            if task.report:
                store_report_embedding(task_id, goal, task.report)

    except Exception as e:
        import traceback
        task = db.query(TaskRecord).filter(TaskRecord.task_id == task_id).first()
        if task:
            task.status = "failed"
            task.error = str(e)
            db.commit()
        print(f"--- TASK {task_id} FAILED ---")
        traceback.print_exc()
    finally:
        db.close()


@app.post("/execute")
async def execute_goal(request: ExecuteRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Receives a goal, creates a task ID, triggers the agent in the background.
    """
    task_id = str(uuid.uuid4())
    
    # First, check if a similar goal exists in ChromaDB
    similar_reports = find_similar_goals(request.goal, n_results=1)
    
    # Initialize task status in DB
    new_task = TaskRecord(
        task_id=task_id,
        goal=request.goal,
        status="running",
        current_node="starting",
        percentage_complete=0,
        retry_count=0
    )
    db.add(new_task)
    db.commit()
    
    # Trigger background execution
    background_tasks.add_task(run_agent_task, task_id, request.goal)
    
    response = {"task_id": task_id, "status": "Task started in background."}
    
    # If a similar report is found, flag it for the frontend
    if similar_reports and similar_reports[0]["distance"] is not None and similar_reports[0]["distance"] < 1.0:
        response["notice"] = "A highly similar goal was previously researched. Check the /similar endpoint."
        
    return response

@app.get("/status/{task_id}")
async def get_status(task_id: str, db: Session = Depends(get_db)):
    """
    Returns current agent status: running node, retry count, percentage.
    """
    task = db.query(TaskRecord).filter(TaskRecord.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    import json
    return {
        "task_id": task.task_id,
        "status": task.status,
        "current_node": task.current_node,
        "percentage_complete": task.percentage_complete,
        "retry_count": task.retry_count,
        "execution_plan": json.loads(task.execution_plan) if task.execution_plan else None,
        "error": task.error
    }


@app.get("/report/{task_id}")
async def get_report(task_id: str, db: Session = Depends(get_db)):
    """
    Returns the completed report once the agent finishes.
    """
    task = db.query(TaskRecord).filter(TaskRecord.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    if task.status == "running":
        return {"message": "Report is still being generated. Check status endpoint."}
    elif task.status == "failed":
        raise HTTPException(status_code=500, detail=f"Task failed: {task.error}")
        
    if not task.report:
        raise HTTPException(status_code=404, detail="Report not found in database.")
        
    return {"task_id": task_id, "report": task.report}


@app.get("/history")
async def get_history(db: Session = Depends(get_db)):
    """
    Returns all past goals and reports from PostgreSQL.
    """
    tasks = db.query(TaskRecord).filter(TaskRecord.status == "completed").all()
    history = []
    for t in tasks:
        history.append({
            "task_id": t.task_id,
            "goal": t.goal,
            "report_snippet": t.report[:100] + "..." if t.report else "",
            "created_at": t.created_at
        })
    return {"history": history}


@app.get("/similar/{task_id}")
async def get_similar_reports(task_id: str, db: Session = Depends(get_db)):
    """
    Checks ChromaDB for semantically similar past reports.
    """
    task = db.query(TaskRecord).filter(TaskRecord.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    similar = find_similar_goals(task.goal)
    
    return {
        "current_goal": task.goal,
        "similar_reports": similar
    }

@app.get("/tasks")
def get_recent_tasks(db: Session = Depends(get_db)):
    """Returns the 10 most recent completed tasks for the history gallery."""
    tasks = db.query(TaskRecord).filter(TaskRecord.status == "completed").order_by(TaskRecord.created_at.desc()).limit(10).all()
    return [
        {
            "task_id": t.task_id,
            "goal": t.goal,
            "created_at": t.created_at.isoformat()
        } for t in tasks
    ]

@app.get("/analytics")
def get_market_analytics(db: Session = Depends(get_db)):
    """Aggregates data across all tasks for the Analytics dashboard."""
    tasks = db.query(TaskRecord).filter(TaskRecord.status == "completed").all()
    
    # Simple mock aggregation logic (in a real app, you'd parse the JSON/text more deeply)
    cities = ["Bangalore", "Hyderabad", "Pune", "Delhi", "Mumbai", "Chennai"]
    skills = ["Python", "React", "Node.js", "AWS", "Machine Learning", "FastAPI", "Docker", "Kubernetes"]
    
    # We simulate trending data based on the number of reports
    count = len(tasks)
    
    return {
        "total_reports": count,
        "active_agents": 6,
        "avg_research_time": "42s",
        "top_cities": [{"name": c, "count": (count * (i+1)) % 15 + 5} for i, c in enumerate(cities)],
        "trending_skills": [{"name": s, "relevance": (count * (i+1)) % 40 + 60} for i, s in enumerate(skills)],
        "tokens_processed": f"{count * 12}.4k"
    }
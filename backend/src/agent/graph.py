from langgraph.graph import StateGraph, END

# Import the shared workflow state structure.
from src.agent.state import AgentState

# Import workflow nodes.
from src.agent.nodes.goal_parser import parse_goal_node
from src.agent.nodes.planner import planner_node
from src.agent.nodes.executor import executor_node
from src.agent.nodes.verifier import verifier_node
from src.agent.nodes.synthesizer import synthesizer_node

from src.agent.nodes.report_generator import report_generator_node

def should_retry(state: AgentState) -> str:
    """
    Conditional routing logic for the Verifier node.
    If the verifier flagged steps to retry, and we haven't hit the limit, route back to executor.
    Otherwise, move forward to synthesizer.
    """
    steps_to_retry = state.get("steps_to_retry")
    retry_count = state.get("retry_count", 0)
    
    if steps_to_retry and retry_count < 3:
        return "executor"
    return "synthesizer"

def human_review_node(state: AgentState):
    """Dummy node to act as a breakpoint for human review."""
    print("--- RUNNING NODE: HUMAN REVIEW ---")
    return {}

def route_after_human_review(state: AgentState) -> str:
    """Routes back to planner if feedback exists, else proceeds to executor."""
    feedback = state.get("verification_feedback")
    if feedback and feedback.lower() != "approved":
        print(f"Human feedback received: {feedback}. Re-routing to planner.")
        return "planner"
    print("Human approved. Proceeding to execution.")
    return "executor"

def create_agent_graph():

    # Create a LangGraph workflow using AgentState as shared memory.
    workflow = StateGraph(AgentState)
    
    # Register the Goal Parser node in the workflow.
    workflow.add_node("goal_parser", parse_goal_node)

    # Register the Planner node in the workflow.
    workflow.add_node("planner", planner_node)
    
    # Register the human review breakpoint node.
    workflow.add_node("human_review", human_review_node)
    
    # Register the Executor node in the workflow.
    workflow.add_node("executor", executor_node)

    # Register the Verifier node in the workflow.
    workflow.add_node("verifier", verifier_node)
    
    # Register the Synthesizer node in the workflow.
    workflow.add_node("synthesizer", synthesizer_node)
    
    # Register the Report Generator node in the workflow.
    workflow.add_node("report_generator", report_generator_node)
    
    # Set the starting node of the workflow.
    workflow.set_entry_point("goal_parser")

    # After Goal Parser finishes, move execution to Planner.
    workflow.add_edge("goal_parser", "planner")

    # After Planner finishes, move execution to human_review.
    workflow.add_edge("planner", "human_review")
    
    # After human_review, conditionally route back to planner or proceed to executor.
    workflow.add_conditional_edges("human_review", route_after_human_review)

    # After Executor finishes, move execution to Verifier.
    workflow.add_edge("executor", "verifier")

    # The Verifier uses conditional edges to decide the next step.
    workflow.add_conditional_edges("verifier", should_retry)
    
    # After Synthesizer finishes, move to Report Generator.
    workflow.add_edge("synthesizer", "report_generator")
    
    # End the workflow after Report Generator finishes.
    workflow.add_edge("report_generator", END)
    
    # Compile the workflow graph into an executable LangGraph application.
    import sqlite3
    from langgraph.checkpoint.sqlite import SqliteSaver
    import os
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Check if we are running in a Docker/cloud environment with a persistent volume
    db_path = os.getenv("DATABASE_PATH")
    if db_path:
        checkpoint_db = os.path.join(os.path.dirname(db_path), "checkpoints.db")
    else:
        checkpoint_db = os.path.join(BASE_DIR, "checkpoints.db")
    
    conn = sqlite3.connect(checkpoint_db, check_same_thread=False)
    memory = SqliteSaver(conn)

    # Interrupt BEFORE the human_review node so we can collect feedback!
    app = workflow.compile(checkpointer=memory, interrupt_before=["human_review"])

    # Return the runnable workflow app.
    return app
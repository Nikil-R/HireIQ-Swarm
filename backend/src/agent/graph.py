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

def create_agent_graph():

    # Create a LangGraph workflow using AgentState as shared memory.
    workflow = StateGraph(AgentState)
    
    # Register the Goal Parser node in the workflow.
    workflow.add_node("goal_parser", parse_goal_node)

    # Register the Planner node in the workflow.
    workflow.add_node("planner", planner_node)
    
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

    # After Planner finishes, move execution to Executor.
    workflow.add_edge("planner", "executor")

    # After Executor finishes, move execution to Verifier.
    workflow.add_edge("executor", "verifier")

    # The Verifier uses conditional edges to decide the next step.
    workflow.add_conditional_edges("verifier", should_retry)
    
    # After Synthesizer finishes, move to Report Generator.
    workflow.add_edge("synthesizer", "report_generator")
    
    # End the workflow after Report Generator finishes.
    workflow.add_edge("report_generator", END)
    
    # Compile the workflow graph into an executable LangGraph application.
    app = workflow.compile()

    # Return the runnable workflow app.
    return app
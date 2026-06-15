from src.agent.state import AgentState, StepResult

from src.agent.tools.search_jobs import search_jobs_tool
from src.agent.tools.extract_skills import extract_skills_tool
from src.agent.tools.rank_skills import rank_skills_tool
from src.agent.tools.fetch_salaries import fetch_salaries_tool
from src.agent.tools.analyze_trends import analyze_trends_tool
from src.agent.tools.fetch_jd import fetch_jd_tool

# Map action strings to real functions
TOOL_MAP = {
    "search_jobs": search_jobs_tool,
    "extract_skills": extract_skills_tool,
    "rank_skills": rank_skills_tool,
    "fetch_salaries": fetch_salaries_tool,
    "analyze_trends": analyze_trends_tool,
    "fetch_jd": fetch_jd_tool
}

def executor_node(state: AgentState) -> AgentState:
    """
    Node 3: Executor
    Executes each step in the execution plan using the appropriate mock tools.
    """
    print("--- RUNNING NODE: EXECUTOR ---")
    
    plan = state.get("execution_plan", [])
    if not plan:
        print("No execution plan found. Skipping execution.")
        return {"execution_results": []}
        
    # Copy existing results so we don't wipe them out on retry
    results = list(state.get("execution_results") or [])
    steps_to_retry = state.get("steps_to_retry") or []
    
    if steps_to_retry:
        print(f"Retrying specific steps: {steps_to_retry}")
        steps_to_run = steps_to_retry
    else:
        steps_to_run = [step.get("step") for step in plan]
    
    for step in plan:
        step_num = step.get("step")
        if step_num not in steps_to_run:
            continue
            
        action = step.get("action")
        description = step.get("description")
        
        feedback = state.get("verification_feedback")
        if feedback:
            description = f"[USER FEEDBACK TO CONSIDER: {feedback}] " + description
            
        print(f"  -> Executing Step {step_num}: {action}...")
        
        tool_func = TOOL_MAP.get(action)
        if tool_func:
            # Call the mocked tool
            result_data = tool_func(description)
        else:
            result_data = f"[ERROR] Unknown action: '{action}'. No tool available."
            
        print(f"     Result: {result_data}")
            
        # Update existing result or append new one
        existing_idx = next((i for i, r in enumerate(results) if r["step"] == step_num), None)
        new_result = StepResult(step=step_num, action=action, result=result_data)
        
        if existing_idx is not None:
            results[existing_idx] = new_result
        else:
            results.append(new_result)
        
    return {"execution_results": results}

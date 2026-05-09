from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List

from src.agent.state import AgentState, PlanStep
from src.config.llm import get_llm

class PlanStepSchema(BaseModel):
    step: int = Field(description="Step number")
    action: str = Field(description="Action to perform (e.g., search_jobs, extract_skills, rank_skills)")
    description: str = Field(description="Detailed description of what the step entails")

class ExecutionPlanSchema(BaseModel):
    plan: List[PlanStepSchema] = Field(description="List of steps to execute the goal")

def planner_node(state: AgentState) -> AgentState:
    """
    Node 2: Planner
    Takes the structured goal and generates a step-by-step execution plan.
    """
    print("--- RUNNING NODE: PLANNER ---")
    
    # 1. Read the structured goal from the state
    structured_goal = state.get("structured_goal")
    
    if not structured_goal:
        return {"execution_plan": []}
    
    # 2. Get our LLM and tell it to output our ExecutionPlanSchema format
    llm = get_llm()
    structured_llm = llm.with_structured_output(ExecutionPlanSchema)
    
    # 3. Create the prompt instructions
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an AI workflow planner.\n"
                   "Given a structured hiring research goal, create a step-by-step execution plan.\n"
                   "Only generate steps relevant to the user's goal. Do not generate unnecessary steps.\n\n"
                   "Each step should contain:\n"
                   "- step number\n"
                   "- action\n"
                   "- description\n\n"
                   "Possible actions you can use:\n"
                   "- search_jobs\n"
                   "- extract_skills\n"
                   "- rank_skills\n"
                   "- fetch_salaries\n"
                   "- analyze_trends\n"
                   "- fetch_jd"),
        ("user", "Structured Goal: {structured_goal}")
    ])
    
    # 4. Chain the prompt to the LLM and run it
    chain = prompt | structured_llm
    result = chain.invoke({"structured_goal": structured_goal})
    print(f"Generated Plan: {result}")
    
    # 5. Convert the Pydantic result into a typed list of PlanStep TypedDicts
    execution_plan: List[PlanStep] = [PlanStep(**p.model_dump()) for p in result.plan]
    
    # 6. Return the updated state
    return {"execution_plan": execution_plan}

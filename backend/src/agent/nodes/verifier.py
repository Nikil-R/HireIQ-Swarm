from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List

from src.agent.state import AgentState
from src.config.llm import get_llm

class VerificationResultSchema(BaseModel):
    is_valid: bool = Field(description="True if the results are complete, specific, and consistent enough to build a report. False otherwise.")
    feedback: str = Field(description="Specific feedback on what is missing or incorrect. Empty if valid.")
    steps_to_retry: List[int] = Field(description="List of step numbers from the execution plan that need to be retried. Empty if valid.")

def verifier_node(state: AgentState) -> AgentState:
    """
    Node 4: Verifier
    Checks the execution results against the structured goal for completeness and quality.
    """
    print("--- RUNNING NODE: VERIFIER ---")
    
    structured_goal = state.get("structured_goal")
    execution_results = state.get("execution_results", [])
    retry_count = state.get("retry_count", 0)
    
    if not execution_results:
        print("No execution results to verify.")
        return {"retry_count": retry_count, "steps_to_retry": []}
        
    llm = get_llm()
    structured_llm = llm.with_structured_output(VerificationResultSchema)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Verification Agent.\n"
                   "Review the provided Structured Goal and Execution Results.\n"
                   "Evaluate if the results are complete, specific enough, and consistent.\n"
                   "If they are good enough to synthesize a final report, set is_valid to true.\n"
                   "If data is missing or vague, set is_valid to false, provide clear feedback, and specify which step numbers need to be retried.\n"
                   "Only retry steps if absolutely necessary. If a tool failed but you have enough context from other steps, proceed."),
        ("user", "Structured Goal:\n{structured_goal}\n\nExecution Results:\n{execution_results}")
    ])
    
    chain = prompt | structured_llm
    result = chain.invoke({
        "structured_goal": structured_goal,
        "execution_results": execution_results
    })
    
    print(f"Verification Pass: {result.is_valid}")
    if not result.is_valid:
        print(f"Feedback: {result.feedback}")
        print(f"Steps to retry: {result.steps_to_retry}")
        
    return {
        "verification_feedback": result.feedback,
        "steps_to_retry": result.steps_to_retry if not result.is_valid else [],
        "retry_count": retry_count + 1
    }

from langchain_core.prompts import ChatPromptTemplate
from src.config.llm import get_llm
from pydantic import BaseModel, Field
from typing import List, Optional
from src.agent.state import AgentState, StructuredGoal

class StructuredGoalSchema(BaseModel):
    """Schema for extracting structured information from a raw goal."""
    goal_type: str = Field(
        description="The type of goal. e.g. 'skill research', 'role comparison', 'company research'"
    )
    subject: List[str] = Field(
        description="The main subjects of the goal. e.g. ['AI Engineer'], ['ML Engineer', 'AI Engineer'], ['Google', 'Microsoft']"
    )
    location: Optional[str] = Field(
        description="The geographical location if specified, else None. e.g. 'Bangalore', 'India'"
    )
    constraints: List[str] = Field(
        description="Any specific constraints or filters mentioned. e.g. ['fresher level', 'remote']"
    )
    expected_output: str = Field(
        description="What the user expects to see as the final result. e.g. 'A ranked list of skills', 'A comparison report'"
    )



def parse_goal_node(state: AgentState) -> AgentState:
    """
    Node 1: Goal Parser
    Takes the raw user input and structures it into a clean object.
    """
    raw_goal = state["raw_goal"]
    
    # Using centralized LLM for structured extraction
    llm = get_llm()
    structured_llm = llm.with_structured_output(StructuredGoalSchema)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert Recruitment Intelligence Analyst.\n"
                   "Your task is to parse the user's raw goal into a structured format.\n"
                   "Extract the type of goal, the main subjects, the location, any constraints, and the expected output.\n"
                   "If a field is not explicitly mentioned, omit it or return an empty list/None as appropriate."),
        ("user", "Raw Goal: {raw_goal}")
    ])
    
    # Creates a LangChain pipeline where the prompt output is passed to the structured Gemini model.
    chain = prompt | structured_llm
    
    # Executes the chain by sending the raw goal to the prompt and getting structured output from the model.
    result = chain.invoke({"raw_goal": raw_goal})
    
    # Maps the structured output from Gemini to the expected AgentState format.
    structured_goal: StructuredGoal = {
        "goal_type": result.goal_type,
        "subject": result.subject,
        "location": result.location,
        "constraints": result.constraints,
        "expected_output": result.expected_output
    }
    
    # Return a dict containing the state update
    return {"structured_goal": structured_goal}
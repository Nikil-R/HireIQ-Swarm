from typing import List
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from src.agent.state import AgentState, ReportSection
from src.config.llm import get_llm

class ReportSectionSchema(BaseModel):
    title: str = Field(description="The title of the insight or report section.")
    content: str = Field(description="The detailed insight, connecting data points and explaining what the data means.")

class SynthesizedInsightsSchema(BaseModel):
    sections: List[ReportSectionSchema] = Field(description="List of synthesized report sections based on the execution results.")

def synthesizer_node(state: AgentState) -> AgentState:
    """
    Node 5: Synthesizer
    Takes all verified execution results and synthesizes them into connected, structured insights.
    """
    print("--- RUNNING NODE: SYNTHESIZER ---")
    
    structured_goal = state.get("structured_goal")
    execution_results = state.get("execution_results", [])
    
    if not execution_results:
        print("No execution results to synthesize.")
        return {"synthesized_insights": []}
        
    llm = get_llm()
    structured_llm = llm.with_structured_output(SynthesizedInsightsSchema)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an Expert Intelligence Synthesizer.\n"
                   "Your job is to read raw execution results and synthesize them into highly actionable insights.\n"
                   "DO NOT just summarize the data. Reason about it. Connect data points together.\n"
                   "Example: 'Skills in high demand but low in candidate profiles = your biggest opportunity.'\n"
                   "Generate structured sections for a final report based ONLY on the data provided.\n"
                   "Make the insights sharp, professional, and highly relevant to the User's Goal."),
        ("user", "User Goal:\n{structured_goal}\n\nRaw Execution Results:\n{execution_results}")
    ])
    
    chain = prompt | structured_llm
    result = chain.invoke({
        "structured_goal": structured_goal,
        "execution_results": execution_results
    })
    
    # Convert Pydantic output to TypedDict list
    insights: List[ReportSection] = [{"title": sec.title, "content": sec.content} for sec in result.sections]
    
    print(f"Generated {len(insights)} synthesized insights.")
    for i, section in enumerate(insights, 1):
        print(f"  Insight {i}: {section['title']}")
        
    return {"synthesized_insights": insights}

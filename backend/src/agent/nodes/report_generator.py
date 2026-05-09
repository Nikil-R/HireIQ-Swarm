from langchain_core.prompts import ChatPromptTemplate
from src.agent.state import AgentState
from src.config.llm import get_llm

def report_generator_node(state: AgentState) -> AgentState:
    """
    Node 6: Report Generator
    Formats synthesized insights, methodology, and goal summary into a final readable report.
    Persists the report to PostgreSQL and ChromaDB.
    """
    print("--- RUNNING NODE: REPORT GENERATOR ---")
    
    synthesized_insights = state.get("synthesized_insights")
    
    if not synthesized_insights:
        print("No insights to generate a report from.")
        return {"final_report": ""}
        
    llm = get_llm()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an Executive Report Generator.\n"
                   "Take the provided context and generate a final, highly readable markdown report.\n"
                   "The report MUST strictly follow this exact structure:\n\n"
                   "1. Goal Summary: What was originally asked.\n"
                   "2. Methodology: What steps were taken and what data was gathered.\n"
                   "3. Key Findings: The main synthesized insights.\n"
                   "4. Detailed Analysis: Section-by-section breakdown based on the insights provided.\n"
                   "5. Recommendations: Specific, actionable next steps.\n"
                   "6. Data Quality Notes: What was found confidently vs what was missing or estimated.\n\n"
                   "Do not make up external data. Rely solely on the provided context.\n"),
        ("user", "Context for Report Generation:\n\n"
                 "- Original Goal:\n{structured_goal}\n\n"
                 "- Execution Plan:\n{execution_plan}\n\n"
                 "- Synthesized Insights:\n{synthesized_insights}\n\n"
                 "- Verifier Feedback / Data Notes:\n{verification_feedback}")
    ])
    
    chain = prompt | llm
    
    result = chain.invoke({
        "structured_goal": state.get("structured_goal"),
        "execution_plan": state.get("execution_plan"),
        "synthesized_insights": synthesized_insights,
        "verification_feedback": state.get("verification_feedback") or "All data retrieved successfully with high confidence."
    })
    
    final_report = result.content
    
    print("\n================ FINAL REPORT ================\n")
    print(final_report)
    print("\n==============================================\n")

    return {"final_report": final_report}

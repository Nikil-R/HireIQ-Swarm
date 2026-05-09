from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List
from src.config.llm import get_llm

class SkillItem(BaseModel):
    skill_name: str = Field(description="The name of the professional skill extracted.")
    frequency: int = Field(description="Estimated frequency or importance level of the skill across the text.")

class ExtractedSkills(BaseModel):
    skills: List[SkillItem] = Field(description="List of extracted skills ranked by frequency.")

def extract_skills_tool(job_descriptions: str) -> str:
    """
    Real tool that uses an LLM to extract and rank skills from raw job descriptions.
    """
    print(f"    [LLM] Extracting skills from provided data...")
    
    try:
        llm = get_llm()
        structured_llm = llm.with_structured_output(ExtractedSkills)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert technical recruiter and data extractor.\n"
                       "Analyze the provided raw job search data (which may contain messy JSON or HTML text).\n"
                       "Extract all professional skills mentioned.\n"
                       "Return a clean, structured list of skills along with an estimated frequency (how often it appears)."),
            ("user", "Raw Job Data:\n{job_descriptions}")
        ])
        
        chain = prompt | structured_llm
        result = chain.invoke({"job_descriptions": job_descriptions[:10000]}) # Limit to 10k chars to save context
        
        if not result or not result.skills:
            return "No specific skills were extracted from the data."
            
        # Format the result back into a readable string
        formatted_result = "Extracted Skills (Ranked):\n"
        for s in sorted(result.skills, key=lambda x: x.frequency, reverse=True):
            formatted_result += f"- {s.skill_name} (Frequency: {s.frequency})\n"
            
        return formatted_result
        
    except Exception as e:
        return f"[ERROR] Skills Extraction Failed: {str(e)}"

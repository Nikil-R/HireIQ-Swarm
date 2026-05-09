from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List
from src.config.llm import get_llm

class RankedSkill(BaseModel):
    skill: str = Field(description="Skill name")
    rank: int = Field(description="Importance rank (1 is highest)")
    justification: str = Field(description="Why it holds this rank")

class RankedSkillsList(BaseModel):
    skills: List[RankedSkill]

def rank_skills_tool(data: str):
    print(f"    [LLM] Ranking skills...")
    try:
        llm = get_llm()
        structured_llm = llm.with_structured_output(RankedSkillsList)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert technical recruiter.\n"
                       "Rank the following list of skills by market importance and demand.\n"
                       "Provide a brief justification for each."),
            ("user", "Skills Data:\n{data}")
        ])
        
        result = (prompt | structured_llm).invoke({"data": data[:10000]})
        
        formatted = "Ranked Skills:\n"
        for s in sorted(result.skills, key=lambda x: x.rank):
            formatted += f"{s.rank}. {s.skill} - {s.justification}\n"
            
        return formatted
    except Exception as e:
        return f"[ERROR] Skill Ranking Failed: {str(e)}"

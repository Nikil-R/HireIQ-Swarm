import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq

# Load environment variables from .env file
load_dotenv()


def get_llm():

    # Read GROQ API key from environment
    groq_api_key = os.getenv("GROQ_API_KEY")

    # Initialize GROQ LLM
    llm = ChatGroq(
        groq_api_key=groq_api_key,
        model="llama-3.3-70b-versatile",
        temperature=0
    )

    return llm
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

from backend.utils.config import GOOGLE_API_KEY,GROQ_API_KEY

groq_llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=GROQ_API_KEY,
    temperature=0.2
)

gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    api_key=GOOGLE_API_KEY,
    temperature=0.2
)
from .config import config

from langchain_groq         import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings


EMBEDDING_MODEL = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-2-preview",
    google_api_key=config.GEMINI_API_KEY,
)


LLM_GEMINI = ChatGoogleGenerativeAI(
    model='gemini-2.5-flash',
    temperature=0.3,
    top_p=0.95,
    google_api_key=config.GEMINI_API_KEY
)


LLM_GROQ = ChatGroq(
    model='llama-3.3-70b-versatile',
    temperature=0.3,
    groq_api_key=config.GROQ_API_KEY
)


SPECIALIST_LLM = LLM_GEMINI.with_fallbacks([LLM_GROQ])

FAST_LLM = ChatGroq(
    model='llama-3.3-70b-versatile',
    temperature=0.0,
    groq_api_key=config.GROQ_API_KEY
)
from .config import config

from langchain_groq         import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings


EMBEDDING_MODEL = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-2-preview",
    google_api_key=config.GEMINI_API_KEY,
)

_LLM_GEMINI = ChatGoogleGenerativeAI(
    model='gemini-2.5-flash',
    temperature=0.3,
    top_p=0.95,
    google_api_key=config.GEMINI_API_KEY
)

def _groq_models(temperature: float) -> list[ChatGroq]:
    return [
        ChatGroq(
            model='llama-3.3-70b-versatile',
            temperature=temperature,
            groq_api_key=api_key,
        )
        for api_key in config.GROQ_API_KEYS
    ]


_SPECIALIST_GROQ_MODELS = _groq_models(temperature=0.3)
SPECIALIST_LLM = _LLM_GEMINI.with_fallbacks(_SPECIALIST_GROQ_MODELS)

_FAST_GROQ_MODELS = _groq_models(temperature=0.0)
if not _FAST_GROQ_MODELS:
    raise RuntimeError("Nenhuma chave Groq válida disponível para o FAST_LLM.")

LLM_GROQ = _SPECIALIST_GROQ_MODELS[0]
FAST_LLM = _FAST_GROQ_MODELS[0].with_fallbacks(_FAST_GROQ_MODELS[1:])

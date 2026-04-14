from dotenv import load_dotenv
import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

from pg_tools import TOOLS
from langchain_groq import ChatGroq

from prompt import (
    ROUTER_PROMPT_COMPLETO,
    FINANCEIRO_PROMPT_COMPLETO,
    AGENDA_PROMPT_COMPLETO,
    ORQUESTRADOR_PROMPT_COMPLETO,
)



load_dotenv()



llm_gemini = ChatGoogleGenerativeAI(
    model='gemini-2.5-flash',
    temperature=0.3,
    top_p=0.95,
    google_api_key=os.getenv('GEMINI_API_KEY')
)

llm_groq = ChatGroq(
    model='llama-3.3-70b-versatile',
    temperature=0.3,
    groq_api_key=os.getenv('GROQ_API_KEY')
)



# llm = llm_gemini.with_fallbacks([llm_groq]) # Por algum motivo minha chave do Gemini não funciona, 100% quebrada
llm = llm_groq



checkpoiner = MemorySaver()
app = create_agent(
    model=llm,
    tools=TOOLS,
    system_prompt=SYSTEM_PROMPT_COMPLETO,
    checkpointer=checkpoiner
)



while 1:
    user_input = input("Digite sua pergunta: ").strip()
    if user_input.lower() in ("killmyself"):
        print("Encerrando o assistente.")
        break

    try:
        resposta = app.invoke(
            {'messages': [{"role": "human", "content": user_input}]},
            config={"configurable": {"thread_id": "meu_id_de_sessao"}})
        print(resposta['messages'][-1].content)
    except Exception as e:
        print(f'Erro: {e}')
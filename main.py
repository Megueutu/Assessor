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


# LLMs Antigos

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

llm_especialista = llm_gemini.with_fallbacks([llm_groq])



llm_rapido = ChatGroq(
    model='llama-3.3-70b-versatile',
    temperature=0.0, # Deve ser determinístico
    groq_api_key=os.getenv('GROQ_API_KEY')
)



router_memory = MemorySaver()



router_app = create_agent( # Possui apenas memória, sem acesso a ferramentas
    model=llm_rapido,
    system_prompt=ROUTER_PROMPT_COMPLETO,
    checkpointer=router_memory
)

financeiro_app = create_agent( # Com TOOLs, mas sem memória
    model=llm_especialista,
    system_prompt=FINANCEIRO_PROMPT_COMPLETO,
    tools=TOOLS,
)

agenda_app = create_agent(
    model=llm_especialista,
    system_prompt=AGENDA_PROMPT_COMPLETO,
)

orquestrador_app = create_agent( # Só formata o JSON da saída (especialista)
    model=llm_rapido,
    system_prompt=ORQUESTRADOR_PROMPT_COMPLETO,
)


EXECUTOR = {
    "financeiro": financeiro_app,
    "agenda": agenda_app,
}



# Primeiro é necessário direcionar a pergunta do usuário para o Router
# que será o responsável por redirecionar a mensagem:
#   1. De volta para o usuário
#

def fluxo_assessor(pergunta_usuario, session_id):
    resposta_router = router_app.invoke(
        {'messages': [{"role": "human", "content": pergunta_usuario}]},
        config={"configurable": {"thread_id": session_id}})
    if not resposta_router.strip().startswith("ROUTE="):
        return resposta_router

    # resposta_orquestrador = orquestrador_app.invoke(
    #     {'messages': [{"role": "human", "content": resposta_router['messages'][-1].content}]},
    #     config={"configurable": {"thread_id": session_id}})
    # # print("Resposta do Orquestrador:", resposta_orquestrador['messages'][-1].content)

    # return resposta_orquestrador['messages'][-1].content



while 1:
    try:
        user_input = input("Digite sua pergunta: ").strip()
        if user_input.lower() in ("killmyself"):
            print("Encerrando o assistente.")
            break

        resposta = fluxo_assessor(pergunta_usuario=user_input, session_id="id_usuario_mas_agora_não_importa")
        print(resposta["message"][-1].content)
    except Exception as e:
        print(f'Erro: {e}')

# resposta = router_app.invoke(
#             {'messages': [{"role": "human", "content": user_input}]},
#             config={"configurable": {"thread_id": "meu_id_de_sessao"}})
#             print(resposta['messages'][-1].content)
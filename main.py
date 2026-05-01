from dotenv import load_dotenv
import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

from langchain_groq import ChatGroq
from tools.Financeiro import TOOLS
from tools.FAQ import faq_retriever

from prompt import (
    ROUTER_PROMPT_COMPLETO,
    FINANCEIRO_PROMPT_COMPLETO,
    AGENDA_PROMPT_COMPLETO,
    ORQUESTRADOR_PROMPT_COMPLETO,
    FAQ_PROMPT_COMPLETO
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

financeiro_app = create_agent(
    model=llm_rapido,
    system_prompt=FAQ_PROMPT_COMPLETO,
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

faq_app = create_agent(
    model=llm_rapido,
    system_prompt=FAQ_PROMPT_COMPLETO,
    tools=[faq_retriever],
)






EXECUTOR = {
    "financeiro": financeiro_app,
    "agenda": agenda_app,
    "faq": faq_app,
}






def fluxo_assessor(pergunta_usuario, session_id):
    # Fluxo do Roteador
    resposta_router = router_app.invoke(
        {'messages': [{"role": "human", "content": pergunta_usuario}]},
        config={"configurable": {"thread_id": session_id}}
    )
    saida_router = resposta_router['messages'][-1].content

    if not saida_router.strip().startswith("ROUTE="):
        return saida_router



    # Caso passe para um especialista
    try:
        print(f"Resposta do Router:\n{saida_router}")

        linhas = saida_router.strip().split("\n")
        rota = None
        pergunta_original = None

        for linha in linhas:
            if linha.startswith("ROUTE="):
                rota = linha.replace("ROUTE=", "").strip()
            elif linha.startswith("PERGUNTA_ORIGINAL="):
                pergunta_original = linha.replace("PERGUNTA_ORIGINAL=", "").strip()

        if rota in EXECUTOR:
            resposta_especialista = EXECUTOR[rota].invoke(
                {'messages': [{"role": "human", "content": pergunta_original}]},
                config={"configurable": {"thread_id": session_id}}
            )
        else:
            return saida_router

    except Exception as e:
        return str(e)



    # Retorno do orquestrador (resposta do especialista formatada)
    resposta_orquestrador = orquestrador_app.invoke(
        {'messages': [{"role": "human", "content": resposta_especialista['messages'][-1].content}]},
        config={"configurable": {"thread_id": session_id}}
    )

    return resposta_orquestrador['messages'][-1].content






os.system('cls' if os.name == 'nt' else 'clear') # Limpando o terminal
while 1:
    try:
        user_input = input("Digite sua pergunta: ").strip()
        if user_input.lower() in ("killmyself"):
            print("Encerrando o assistente.")
            break

        resposta = fluxo_assessor(pergunta_usuario=user_input, session_id="id_usuario_mas_agora_não_importa")
        print("🤖 > " + resposta + "\n")
    except Exception as e:
        print(f'Erro: {e}')
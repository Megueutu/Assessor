from agents.router import ROUTER_AGENT
from app.agents.doer import DOER
from app.agents.orchestrator import ORCHESTRATOR_AGENT

def assessor_flow(pergunta_usuario, session_id):
    resposta_router = ROUTER_AGENT.invoke(
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

        if rota in DOER:
            resposta_especialista = DOER[rota].invoke(
                {'messages': [{"role": "human", "content": pergunta_original}]},
                config={"configurable": {"thread_id": session_id}}
            )
        else:
            return saida_router

    except Exception as e:
        return str(e)



    # Retorno do orquestrador (resposta do especialista formatada)
    resposta_orquestrador = ORCHESTRATOR_AGENT.invoke(
        {'messages': [{"role": "human", "content": resposta_especialista['messages'][-1].content}]},
        config={"configurable": {"thread_id": session_id}}
    )

    return resposta_orquestrador['messages'][-1].content
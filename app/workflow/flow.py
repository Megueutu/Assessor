from app.agents.registry import SPECIALIST_AGENTS

from app.agents.router import ROUTER_AGENT
from app.agents.orchestrator import ORCHESTRATOR_AGENT


def parse_router_output(router_text: str):
    if not router_text.strip().startswith("ROUTE="):
        return None, None, router_text

    rota = None
    pergunta_original = None

    for linha in router_text.strip().splitlines():
        if linha.startswith("ROUTE="):
            rota = linha.replace("ROUTE=", "").strip()
        elif linha.startswith("PERGUNTA_ORIGINAL="):
            pergunta_original = linha.replace("PERGUNTA_ORIGINAL=", "").strip()

    return rota, pergunta_original, None


def route_request(pergunta_usuario: str, session_id: str) -> str:
    resposta_router = ROUTER_AGENT.invoke(
        {"messages": [{"role": "human", "content": pergunta_usuario}]},
        config={"configurable": {"thread_id": session_id}},
    )
    return resposta_router["messages"][-1].content



def run_specialist(rota: str, pergunta_original: str, session_id: str):
    specialist_agent = SPECIALIST_AGENTS.get(rota)
    if specialist_agent is None:
        return None

    resposta_especialista = specialist_agent.invoke(
        {"messages": [{"role": "human", "content": pergunta_original}]},
        config={"configurable": {"thread_id": session_id}},
    )
    return resposta_especialista["messages"][-1].content


def format_response(resposta_especialista: str, session_id: str) -> str:
    resposta_orquestrador = ORCHESTRATOR_AGENT.invoke(
        {"messages": [{"role": "human", "content": resposta_especialista}]},
        config={"configurable": {"thread_id": session_id}},
    )
    return resposta_orquestrador["messages"][-1].content


def assessor_flow(pergunta_usuario: str, session_id: str) -> str:
    saida_router = route_request(pergunta_usuario, session_id)
    rota, pergunta_original, resposta_direta = parse_router_output(saida_router)

    if resposta_direta is not None:
        return resposta_direta

    if rota is None or pergunta_original is None:
        return saida_router

    resposta_especialista = run_specialist(rota, pergunta_original, session_id)
    if resposta_especialista is None:
        return saida_router

    return format_response(resposta_especialista, session_id)

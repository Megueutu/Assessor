from app.agents.registry import SPECIALIST_AGENTS
from app.agents.router import ROUTER_AGENT
from app.agents.orchestrator import ORCHESTRATOR_AGENT


def parse_router_output(router_text: str):
    # Caso seja resposta direta
    if not router_text.strip().startswith("ROUTE="):
        return None, None, router_text

    # Caso haja rota, extrai rota e pergunta original
    route, original_question = None, None

    for line in (router_text.strip().splitlines()):
        if line.startswith("ROUTE="):
            route = line.replace("ROUTE=", "").strip()

        elif line.startswith("PERGUNTA_ORIGINAL="):
            original_question = line.replace("PERGUNTA_ORIGINAL=", "").strip()

    return route, original_question, None


def route_request(user_question: str, session_id: str) -> str:
    resposta_router = ROUTER_AGENT.invoke(
        {"messages": [{"role": "human", "content": user_question}]},
        config={"configurable": {"thread_id": session_id}},
    )
    return resposta_router["messages"][-1].content


def run_specialist(route: str, original_question: str, session_id: str):
    specialist_agent = SPECIALIST_AGENTS.get(route)
    if specialist_agent is None:
        return None

    specialist_answer = specialist_agent.invoke(
        {"messages": [{"role": "human", "content": original_question}]},
        config={"configurable": {"thread_id": session_id}},
    )
    return specialist_answer["messages"][-1].content


def format_response(specialist_answer: str, session_id: str) -> str:
    resposta_orquestrador = ORCHESTRATOR_AGENT.invoke(
        {"messages": [{"role": "human", "content": specialist_answer}]},
        config={"configurable": {"thread_id": session_id}},
    )
    return resposta_orquestrador["messages"][-1].content


def assessor_flow(user_question: str, session_id: str) -> str:
    router_output = route_request(user_question, session_id)
    route, original_question, direct_answer = parse_router_output(router_output)

    if direct_answer is not None:
        return direct_answer

    if route is None or original_question is None: # Resposta direta do Router
        return router_output

    specialist_answer = run_specialist(route, original_question, session_id)
    if specialist_answer is None:
        return router_output

    return format_response(specialist_answer, session_id)

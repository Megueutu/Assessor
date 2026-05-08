import json

from app.workflow.target     import Target
from app.agents.router       import ROUTER_AGENT
from app.agents.registry     import SPECIALIST_AGENTS
from app.agents.orchestrator import ORCHESTRATOR_AGENT


def _format_router_answer(text: str) -> dict:
    output = {}
    last_key = None
    for line in text.strip().splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            last_key = key.strip()
            output[last_key] = value.strip()
        elif last_key is not None and line.strip():
            output[last_key] += " " + line.strip()
    return output


def route_request(user_question: str, session_id: str) -> dict[str, str]:
    router_answer = ROUTER_AGENT.invoke(
        {"messages": [{"role": "human", "content": user_question}]},
        config={"configurable": {"thread_id": session_id}},
    )
    return _format_router_answer(router_answer["messages"][-1].content)


def run_specialist(router_output: dict, session_id: str):
    specialist_agent = SPECIALIST_AGENTS.get(router_output.get("ROUTE"))
    if specialist_agent is None:
        return None

    payload = { # Excluíndo as chaves de roteamento
        k: v for k, v in router_output.items()
        if k not in {"TARGET", "ROUTE"}}
    
    content = json.dumps(payload, ensure_ascii=False, indent=2)

    specialist_answer = specialist_agent.invoke(
        {"messages": [{"role": "human", "content": content}]},
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

    if router_output.get("TARGET") == Target.DIRECT:
        return router_output.get("ANSWER")

    specialist_answer = run_specialist(router_output, session_id)
    if specialist_answer is None:
        return router_output

    return format_response(specialist_answer, session_id)

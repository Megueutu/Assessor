from langchain_core.messages import RemoveMessage
from langchain_core.runnables import RunnableConfig

from app.core.constants.agents import Agent
from app.core.constants.flow import Flow
from app.agents.registry import AGENTS, ROUTER_DECISION
from app.workflow.guardrail.guardrail import guardrail_in, guardrail_out
from app.workflow.guardrail.io import anonymize_input
from app.workflow.state import GraphState


def router_node(state: GraphState, config: RunnableConfig) -> dict:
    decision = ROUTER_DECISION(state["messages"], config=config)

    if decision.flow == Flow.DIRECT:
        if not decision.answer:
            raise ValueError("Router retornou DIRECT sem answer.")

        return {
            "flow": Flow.DIRECT.value,
            "messages": [
                {
                    "role": "assistant",
                    "content": decision.answer
                }
            ]
        }

    return {
        "flow": decision.flow,
        "intent": decision.intent
    }


def orchestrator_node(state: GraphState) -> dict:
    output = AGENTS[Agent.ORCHESTRATOR].invoke({"messages": state["messages"]})

    return {
        "messages": [{"role": "assistant", "content": output["messages"][-1].content}],
        "called": [Agent.ORCHESTRATOR],
    }


def guardrail_in_node(state: GraphState) -> dict:
    human_message = list(state["messages"])[-1]

    texto_anonimizado, mapa = anonymize_input(human_message.text)
    resultado = guardrail_in(texto_anonimizado)

    if resultado["bloqueado"]:
        return {
            "messages": [{"role": "assistant", "content": resultado["mensagem"]}],
            "flow": Flow.DIRECT.value,
            "map_pii": {},
            "called": [f"guardrail_in:{resultado['motivo']}"],
        }

    return {
        "messages": [
            RemoveMessage(id=human_message.id),
            {"role": "human", "content": texto_anonimizado},
        ],
        "map_pii": mapa,
        "called": ["guardrail_in:aprovado"],
    }


def guardrail_out_node(state: GraphState) -> dict:
    ultima = ""
    for msg in reversed(state["messages"]):
        if msg.type == "ai" and msg.content:
            ultima = msg.content
            break

    resultado = guardrail_out(ultima, state.get("map_pii", {}))

    return {
        "messages": [{"role": "assistant", "content": resultado["conteudo"]}],
        "called": ["guardrail_out"],
    }

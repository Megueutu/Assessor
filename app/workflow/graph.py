import operator

from typing              import Annotated
from langgraph.graph     import StateGraph, MessagesState, END

from langgraph.checkpoint.memory import MemorySaver
from app.agents.registry         import AGENTS


MEMORY = MemorySaver()


class GraphState(MessagesState):
    messages: list[dict[str, str], operator.add]
    called: Annotated[list[str], operator.add]
    routes: Annotated[list[str], operator.add]


def router_node(state: GraphState) -> dict:
    saida = AGENTS["router"].invoke(
        {"messages": [{"role": "human", "content": state["input"]}]},
        config={"configurable": {"thread_id": state["session_id"]}},
    )
    texto = saida["messages"][-1].text

    if not texto.strip().startswith("ROUTE="):
        return {
            "called": ["router"],
            "final_response":   texto,
        }

    return {
        "input":            texto,
        "called": ["router"],
    }


def orchestrator_node(state: GraphState) -> dict:
    saida = AGENTS["orchestrator"].invoke(
        {"messages": [{"role": "human", "content": state["saida_especialista"]}]},
        config={"configurable": {"thread_id": {state['session_id']}}},
    )
    return {
        "final_response":   saida["messages"][-1].text,
        "called": ["orchestrator"],
    }


def decide_agent(state: GraphState) -> str:
    """Lê o protocolo do roteador e devolve o nome do próximo nó."""
    texto = state["input"].strip()

    if not texto.startswith("ROUTE="):
        return "fim"

    rota = texto.split("\n", 1)[0].split("=", 1)[1].strip()
    return rota if rota in ("financeiro", "agenda", "faq") else "fim"


GRAPH = StateGraph(GraphState)

GRAPH.add_node("router", router_node)
GRAPH.add_node("orchestrator", orchestrator_node)
GRAPH.add_node("financial", AGENTS["financial"])
GRAPH.add_node("schedule", AGENTS["schedule"])
GRAPH.add_node("faq", AGENTS["faq"])

GRAPH.set_entry_point("router")

GRAPH.add_conditional_edges(
    "router",
    decide_agent,
    {
        "financeiro": "financial",
        "agenda":     "schedule",
        "faq":        "faq",
        "fim":        END,
    },
)

GRAPH.add_edge("financial", "orchestrator")
GRAPH.add_edge("schedule", "orchestrator")

GRAPH.add_edge("orchestrator", END)
GRAPH.add_edge("faq", END)

AGENTS_WORKFLOW = GRAPH.compile(checkpointer=MEMORY)
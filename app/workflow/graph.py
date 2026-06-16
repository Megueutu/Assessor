import operator
from typing import Annotated

from langgraph.graph import StateGraph, MessagesState, END
from langgraph.types import Send
from langgraph.checkpoint.memory import MemorySaver

from app.core.constants.agents import Agent
from app.core.constants.flow import Flow 
from app.agents.registry import AGENTS, DEFS


class GraphState(MessagesState):
    called: Annotated[list[str], operator.add]
    intent: Annotated[dict[str, bool], operator.or_]
    specialist_outputs: Annotated[list[str], operator.add]
    flow: str
    map_pii: dict


def router_node(state: GraphState) -> dict:
    decision = DEFS["router"](state["messages"])

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
        "messages": [{"role": "assistant", "content": output["messages"][-1].text}],
        "called": [Agent.ORCHESTRATOR],
    }


def dispatch(state: GraphState):
    sends, flow, intent = list(), state["flow"], state["intent"]

    if flow == Flow.DIRECT: return END

    elif flow == Flow.SPECIALIST:
        if intent.get(Agent.FINANCIAL): sends.append(Send(Agent.FINANCIAL, state))
        if intent.get(Agent.SCHEDULE):  sends.append(Send(Agent.SCHEDULE, state))
        if intent.get(Agent.NOTES):  sends.append(Send(Agent.NOTES, state))

    elif flow == Flow.REFER:
        if intent.get(Agent.FAQ): sends.append(Send(Agent.FAQ, state))

    return sends


GRAPH = StateGraph(GraphState)

GRAPH.add_node(Agent.GUARDRAIL_IN, guardrail_in_node)
GRAPH.add_node(Agent.GUARDRAIL_OUT, guardrail_out_node)
GRAPH.add_conditional_edges(
    Agent.GUARDRAIL_IN,
    guardrail_dispatch,
    {
        Agent.ROUTER,
        END
    }
)

GRAPH.add_node(Agent.ROUTER, router_node)
GRAPH.add_node(Agent.ORCHESTRATOR, orchestrator_node)

GRAPH.set_entry_point(Agent.GUARDRAIL_IN)
GRAPH.add_node("join", lambda _: {})

GRAPH.add_node(Agent.FINANCIAL, AGENTS[Agent.FINANCIAL])
GRAPH.add_node(Agent.SCHEDULE,  AGENTS[Agent.SCHEDULE])
GRAPH.add_node(Agent.NOTES,     AGENTS[Agent.NOTES])
GRAPH.add_node(Agent.FAQ,       AGENTS[Agent.FAQ])

GRAPH.add_conditional_edges(
    Agent.ROUTER,
    dispatch
)

GRAPH.add_edge(Agent.FINANCIAL, "join")
GRAPH.add_edge(Agent.SCHEDULE,  "join")
GRAPH.add_edge(Agent.NOTES,     "join")
GRAPH.add_edge(Agent.FAQ, "join") # FAQ também retorna ao orquestrador

GRAPH.add_edge("join", Agent.ORCHESTRATOR)
GRAPH.add_edge(Agent.GUARDRAIL_OUT, END)
GRAPH.add_edge(Agent.ORCHESTRATOR, END)


MEMORY = MemorySaver()
AGENTS_WORKFLOW = GRAPH.compile(checkpointer=MEMORY)
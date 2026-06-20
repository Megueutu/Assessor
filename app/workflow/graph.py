from langgraph.graph import StateGraph, END
from langgraph.types import Send
from langgraph.checkpoint.memory import MemorySaver

from app.core.constants.agents import Agent
from app.core.constants.flow import Flow
from app.agents.agents import AGENTS

from app.workflow.state import GraphState
from app.workflow.nodes import (
    router_node,
    orchestrator_node,
    guardrail_in_node,
    guardrail_out_node,
)


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


def guardrail_dispatch(state: GraphState):
    return END if state["flow"] == Flow.DIRECT.value else Agent.ROUTER


GRAPH = StateGraph(GraphState)

GRAPH.add_node(Agent.GUARDRAIL_IN, guardrail_in_node)
GRAPH.add_node(Agent.GUARDRAIL_OUT, guardrail_out_node)
GRAPH.add_conditional_edges(
    Agent.GUARDRAIL_IN,
    guardrail_dispatch,
    {
        Agent.ROUTER: Agent.ROUTER,
        END: END,
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
GRAPH.add_edge(Agent.FAQ, "join")

GRAPH.add_edge("join", Agent.ORCHESTRATOR)
GRAPH.add_edge(Agent.ORCHESTRATOR, Agent.GUARDRAIL_OUT)
GRAPH.add_edge(Agent.GUARDRAIL_OUT, END)


MEMORY = MemorySaver()
AGENTS_WORKFLOW = GRAPH.compile(checkpointer=MEMORY)

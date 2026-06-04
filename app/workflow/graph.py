import operator
from typing import Annotated

from langgraph.graph import StateGraph, MessagesState, END
from langgraph.constants import Send
from langgraph.checkpoint.memory import MemorySaver

from app.workflow.nodes import orchestrator_node, router_node
from app.core.constants.agents import Agent
from app.core.constants.flow import Flow 
from app.agents.registry import AGENTS


class GraphState(MessagesState):
    called: Annotated[list[str], operator.add]
    intent: Annotated[dict[str, bool], operator.or_]
    flow: Flow


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


def decide_flow(state: GraphState) -> str:
    if state["flow"]   == Flow.DIRECT:     return Flow.DIRECT
    elif state["flow"] == Flow.SPECIALIST: return Flow.SPECIALIST
    elif state["flow"] == Flow.REFER:      return Flow.REFER

    raise Exception("Something went wrong with the system.")


GRAPH, PLANNER = StateGraph(GraphState), "planner"

GRAPH.add_node(Agent.ROUTER, router_node)
GRAPH.add_node(Agent.ORCHESTRATOR, orchestrator_node)

GRAPH.set_entry_point(Agent.ROUTER)

GRAPH.add_node(Agent.FINANCIAL, AGENTS[Agent.FINANCIAL])
GRAPH.add_node(Agent.SCHEDULE,  AGENTS[Agent.SCHEDULE])
GRAPH.add_node(Agent.NOTES,     AGENTS[Agent.NOTES])
GRAPH.add_node(Agent.FAQ,       AGENTS[Agent.FAQ])

GRAPH.add_conditional_edges(
    Agent.ROUTER,
    decide_flow,
    {
        Flow.SPECIALIST: PLANNER,
        Flow.REFER: PLANNER,
        Flow.DIRECT: END,
    },
)

GRAPH.add_conditional_edges(
    PLANNER,
    dispatch
)

GRAPH.add_edge(Agent.FINANCIAL, Agent.ORCHESTRATOR)
GRAPH.add_edge(Agent.SCHEDULE,  Agent.ORCHESTRATOR)
GRAPH.add_edge(Agent.NOTES,     Agent.ORCHESTRATOR)
GRAPH.add_edge(Agent.FAQ, Agent.ORCHESTRATOR) # FAQ também retorna ao orquestrador

GRAPH.add_edge(Agent.ORCHESTRATOR, END)


MEMORY = MemorySaver()
AGENTS_WORKFLOW = GRAPH.compile(checkpointer=MEMORY)
from app.core.constants.flow import Flow 
from app.agents.registry import AGENTS, DEFS
from app.workflow.graph import GraphState

def router_node(state: GraphState) -> dict:
    user_question = state["messages"][-1].content
    decision = DEFS["ROUTER"](user_question)

    if decision.flow == Flow.DIRECT:
        return {
            "flow": Flow.DIRECT,
            "messages": [{"role": "assistant", "content": decision.answer}]
        }

    return {
        "flow": decision.flow,
        "intent": decision.intent
    }


def orchestrator_node(state: GraphState) -> dict:
    saida = AGENTS["orchestrator"].invoke(
        {"messages": state["messages"]},
        config={"configurable": {"thread_id": {state['session_id']}}},
    )
    return {
        "final_response":   saida["messages"][-1].text,
        "called": ["orchestrator"],
    }
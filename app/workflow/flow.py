from app.workflow.graph import AGENTS_WORKFLOW

def assessor_flow(user_question: str, session_id: str) -> str:
    result = AGENTS_WORKFLOW.invoke(
        {"messages": [{"role": "human", "content": user_question}]},
        config={"configurable": {"thread_id": session_id}}
        )

    return result["messages"][-1].content

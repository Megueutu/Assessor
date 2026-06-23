from app.workflow.graph import AGENTS_WORKFLOW
from app.workflow.guardrail.io import *
from app.database.sessions import salvar_mensagem

def assessor_flow(user_question: str, session_id: str) -> str:
    anonymized_message, mapp = anonymize_input(user_question)
    
    result = AGENTS_WORKFLOW.invoke(
        {
            "messages": [{"role": "human", "content": anonymized_message}],
            "called": [],
            "intent": {},
            "specialist_outputs": [],
            "flow": "",
            "map_pii": mapp,
        },
        config={"configurable": {"thread_id": session_id}}
        )

    return result["messages"][-1].content

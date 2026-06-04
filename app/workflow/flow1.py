from app.workflow.graph import AGENTS_WORKFLOW

def executar_fluxo_assessor(pergunta_usuario: str, session_id: str) -> str:
    estado_inicial = {
        "input":              pergunta_usuario,
        "session_id":         session_id,
        "agentes_chamados":   [],
        "saida_especialista": "",
        "resposta_final":     "",
    }

    estado_final = AGENTS_WORKFLOW.invoke(
        estado_inicial,
        config={"configurable": {"thread_id": session_id}},
    )

    print(f"[debug] agentes chamados: {estado_final['agentes_chamados']}")
    return estado_final["resposta_final"]

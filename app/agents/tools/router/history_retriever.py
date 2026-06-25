from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from app.database.history import retrieve_history

@tool
def history_retriever(search: str, config: RunnableConfig) -> str:
    """Consulta conversas ANTERIORES do usuário (sessões já encerradas).

    Use SOMENTE quando a resposta depende de algo dito numa conversa passada
    — preferências, decisões ou planos que o usuário mencionou antes.
    NÃO use para dados que estão no banco (gastos, saldos, eventos): para isso
    já existem as tools de consulta específicas como query_transactions, total_balance, daily_balance.

    Args:
        busca: assunto a procurar nos resumos das conversas anteriores.
    """
    session_id = config["configurable"]["thread_id"]
    historico  = retrieve_history(session_id, search, limit=3)

    if not historico:
        return "Nenhuma conversa anterior relevante encontrada."

    return "\n\n".join(
        f"[{h['iniciada_em']:%d/%m/%Y}] {h['resumo']}" for h in historico
    )
from langchain.tools import tool
from typing import Optional

from app.tools.response import ToolResponse
from app.tools.notes.args import AddNoteArgs
from app.core.database import get_cursor
from app.core.llms import FAST_LLM


_SQL = """
INSERT INTO notes (source_text, content, items)
VALUES (%s, %s, %s)
RETURNING id, content, items, recorded_at
"""


@tool("add_note", args_schema=AddNoteArgs)
def add_note(source_text: str, items: Optional[list[str]] = None) -> dict:
    """Cria uma nova nota ou checklist para o usuário com base em sua mensagem."""

    try:
        content = FAST_LLM.invoke(f"Resuma e corrija ortograficamente: '{source_text}'.\nResponda só com o resumo.").content.strip()
    
    except Exception as e:
        return ToolResponse.error(message=f"Erro ao processar resumo da mensagem: {e}")


    try:
        with get_cursor() as (_, cur):
            cur.execute(_SQL, (source_text, content, items))
            SQL_RETURN = cur.fetchone()

        return ToolResponse.ok(
            sql_return={
                "note_id":     SQL_RETURN[0],
                "content":     SQL_RETURN[1],
                "items":       SQL_RETURN[2],
                "recorded_at": SQL_RETURN[3].isoformat()
            }
        )

    except Exception as e:
        return ToolResponse.error(message=f"Erro ao salvar nota no banco de dados: {e}")
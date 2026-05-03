from pydantic import BaseModel, Field
from typing import Optional


class AddNoteArgs(BaseModel):
    source_text:  str            = Field(...,           description="Texto original do usuário.")
    item:         Optional[str]  = Field(default=None,  description="Item associado à nota.")


class ConcludeNoteArgs(BaseModel):
    note_id: int  = Field(..., description="ID da nota a ser concluída.")

    
class ListNotesArgs(BaseModel):
    note_id:   Optional[int]       = Field(default=None, description="Filtro por ID da nota.")
    content:   Optional[str]       = Field(default=None, description="Texto para filtrar notas por conteúdo da nota (resumo da nota).")
    itens:     Optional[list[str]] = Field(default=None, description="Texto para filtrar notas por itens listados.")
    state:     Optional[bool]      = Field(default=None, description="Filtrar por estado de conclusão (concluída ou não).")
    limit:     Optional[int]       = Field(default=20,   description="Número máximo de notas a serem listadas.")
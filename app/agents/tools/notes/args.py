from typing import Literal, Optional

from pydantic import BaseModel, Field


NoteStatus = Literal["ACTIVE", "COMPLETED", "ARCHIVED"]
WishStatus = Literal["ACTIVE", "PURCHASED", "CANCELLED", "ARCHIVED"]


class AddNoteArgs(BaseModel):
    source_text: str = Field(..., min_length=1, description="Texto original do usuário.")
    title: Optional[str] = Field(default=None, description="Título curto da anotação.")
    content: Optional[str] = Field(default=None, description="Conteúdo organizado da anotação.")
    category_name: Optional[str] = Field(default=None, description="Categoria compartilhada com finanças e desejos.")
    items: Optional[list[str]] = Field(default=None, description="Itens do checklist, quando houver.")


class ListNotesArgs(BaseModel):
    note_id: Optional[int] = Field(default=None, gt=0, description="ID da nota.")
    content: Optional[str] = Field(default=None, description="Texto presente no título, conteúdo ou texto original.")
    items: Optional[list[str]] = Field(default=None, description="Itens que devem existir no checklist.")
    status: Optional[NoteStatus] = Field(default=None, description="Estado da nota.")
    category_name: Optional[str] = Field(default=None, description="Nome da categoria.")
    limit: int = Field(default=20, ge=1, le=100, description="Número máximo de notas.")


class UpdateNoteArgs(BaseModel):
    note_id: int = Field(..., gt=0, description="ID da nota.")
    title: Optional[str] = Field(default=None, description="Novo título.")
    content: Optional[str] = Field(default=None, description="Novo conteúdo.")
    category_name: Optional[str] = Field(default=None, description="Nova categoria.")
    status: Optional[NoteStatus] = Field(default=None, description="Novo estado.")


class ConcludeNoteArgs(BaseModel):
    note_id: int = Field(..., gt=0, description="ID da nota a concluir.")


class AddNoteItemArgs(BaseModel):
    note_id: int = Field(..., gt=0, description="ID da nota.")
    content: str = Field(..., min_length=1, description="Conteúdo do novo item.")


class CompleteNoteItemArgs(BaseModel):
    item_id: int = Field(..., gt=0, description="ID do item do checklist.")


class AddWishArgs(BaseModel):
    name: str = Field(..., min_length=1, description="Nome do item desejado.")
    source_text: str = Field(..., min_length=1, description="Texto original do usuário.")
    description: Optional[str] = Field(default=None, description="Detalhes do desejo.")
    category_name: Optional[str] = Field(default=None, description="Categoria do desejo.")
    target_amount: Optional[float] = Field(default=None, gt=0, description="Valor alvo opcional.")
    priority: Optional[int] = Field(default=None, ge=1, le=5, description="Prioridade de 1 a 5.")


class ListWishesArgs(BaseModel):
    wish_id: Optional[int] = Field(default=None, gt=0, description="ID do desejo.")
    search: Optional[str] = Field(default=None, description="Texto presente no nome ou descrição.")
    status: Optional[WishStatus] = Field(default=None, description="Estado do desejo.")
    category_name: Optional[str] = Field(default=None, description="Nome da categoria.")
    limit: int = Field(default=20, ge=1, le=100, description="Número máximo de desejos.")


class UpdateWishArgs(BaseModel):
    wish_id: int = Field(..., gt=0, description="ID do desejo.")
    name: Optional[str] = Field(default=None, description="Novo nome.")
    description: Optional[str] = Field(default=None, description="Nova descrição.")
    category_name: Optional[str] = Field(default=None, description="Nova categoria.")
    target_amount: Optional[float] = Field(default=None, gt=0, description="Novo valor alvo.")
    priority: Optional[int] = Field(default=None, ge=1, le=5, description="Nova prioridade.")


class CancelWishArgs(BaseModel):
    wish_id: int = Field(..., gt=0, description="ID do desejo a cancelar.")


class FindMatchingWishesArgs(BaseModel):
    search: str = Field(..., min_length=2, description="Descrição do item comprado.")
    category_name: Optional[str] = Field(default=None, description="Categoria da compra.")
    limit: int = Field(default=5, ge=1, le=10, description="Máximo de candidatos.")

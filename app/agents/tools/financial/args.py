from pydantic import BaseModel, Field
from typing import Literal, Optional


class BaseModelTransaction(BaseModel):
    source_text: Optional[str] = Field(default=None, description="Texto original do usuário.")
    type_name:   Optional[str] = Field(default=None, description="Tipo da transação: INCOME | EXPENSES | TRANSFER.")


class AddTransactionArgs(BaseModelTransaction):
    source_text:    str           = Field(..., min_length=1, description="Texto original do usuário.")
    amount:         float         = Field(..., gt=0, description="Valor da transação.")
    occurred_at:    Optional[str] = Field(default=None, description="Timestamp ISO 8601; se ausente, usa NOW() no banco.")
    type_id:        Optional[int] = Field(default=None, description="ID em transaction_types (1=INCOME, 2=EXPENSES, 3=TRANSFER).",)
    category_id:    Optional[int] = Field(default=None, description="FK de categories (opcional).")
    category_name:  Optional[str] = Field(default=None, description="Nome da categoria: comida, transporte, moradia, saúde, lazer, contas, besteira, estudo, férias, investimento, presente, eletrônicos, outros.",)
    description:    Optional[str] = Field(default=None, description="Descrição (opcional).")
    payment_method: Optional[str] = Field(default=None, description="Forma de pagamento (opcional).")


class QueryTransactionsArgs(BaseModelTransaction):
    date_from_local: Optional[str] = Field(default=None, description="Data inicial (YYYY-MM-DD) no fuso de São Paulo.")
    date_to_local:   Optional[str] = Field(default=None, description="Data final (YYYY-MM-DD) no fuso de São Paulo.")
    category_name:   Optional[str] = Field(default=None, description="Nome da categoria (ex: COMIDA, TRANSPORTE).")


class UpdateTransactionArgs(BaseModel):
    id:             Optional[int]   = Field(default=None, description="ID da transação a atualizar. Se ausente, será feita uma busca por (match_text + date_local).",)
    match_text:     Optional[str]   = Field(default=None, description="Texto para localizar transação quando id não for informado (busca em source_text/description).",)
    date_local:     Optional[str]   = Field(default=None, description="Data local (YYYY-MM-DD) em America/Sao_Paulo; usado em conjunto com match_text quando id ausente.",)
    amount:         Optional[float] = Field(default=None, gt=0, description="Novo valor.")
    type_id:        Optional[int]   = Field(default=None, description="Novo type_id (1/2/3).")
    type_name:      Optional[str]   = Field(default=None, description="Novo type_name: INCOME | EXPENSES | TRANSFER.")
    category_id:    Optional[int]   = Field(default=None, description="Nova categoria (id).")
    category_name:  Optional[str]   = Field(default=None, description="Nova categoria (nome).")
    description:    Optional[str]   = Field(default=None, description="Nova descrição.")
    payment_method: Optional[str]   = Field(default=None, description="Novo meio de pagamento.")
    occurred_at:    Optional[str]   = Field(default=None, description="Novo timestamp ISO 8601.")


class PurchaseWishArgs(BaseModel):
    wish_id: int = Field(..., gt=0, description="ID do desejo confirmado pelo usuário.")
    amount: float = Field(..., gt=0, description="Valor pago.")
    source_text: str = Field(..., min_length=1, description="Texto original em que o usuário confirmou a compra.")
    confirmation: Literal["CONFIRMO"] = Field(..., description="Confirmação explícita. Use somente após o usuário confirmar o vínculo.")
    occurred_at: Optional[str] = Field(default=None, description="Timestamp ISO 8601; se ausente, usa NOW().")
    category_name: Optional[str] = Field(default=None, description="Categoria da compra.")
    description: Optional[str] = Field(default=None, description="Descrição da transação.")
    payment_method: Optional[str] = Field(default=None, description="Forma de pagamento.")

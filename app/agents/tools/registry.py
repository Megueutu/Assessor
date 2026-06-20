from . import (
    daily_balance,
    total_balance,
    add_transaction,
    search_transactions,
    update_transaction,
    faq_retriever,
    add_note,
    conclude_note,
    list_notes,
)

FINANCIAL_TOOLS = [
    daily_balance,
    total_balance,
    add_transaction,
    search_transactions,
    update_transaction,
]

FAQ_TOOLS = [
    faq_retriever,
]

NOTES_TOOLS = [
    add_note,
    conclude_note,
    list_notes,
]
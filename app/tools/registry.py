from .financial.tools.balance import daily_balance, total_balance
from .financial.tools.transaction import add_transaction, search_transaction, update_transaction
from .notes.tools import add_note, conclude_note, list_notes
from .faq import faq_retriever


FINANCIAL_TOOLS = [
    daily_balance,
    total_balance,
    add_transaction,
    search_transaction,
    update_transaction,
]

FAQ_TOOLS = [
    faq_retriever
]

NOTES_TOOLS = [
    add_note,
    conclude_note,
    list_notes
]
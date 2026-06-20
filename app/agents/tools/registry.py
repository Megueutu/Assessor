from .financial.balance.daily_balance import daily_balance
from .financial.balance.total_balance import total_balance
from .financial.transaction.add_transaction import add_transaction
from .financial.transaction.search_transactions import search_transactions
from .financial.transaction.update_transaction import update_transaction
from .faq.faq_retriever import faq_retriever
from .notes.note.add_note import add_note
from .notes.note.conclude_note import conclude_note
from .notes.note.list_notes import list_notes

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
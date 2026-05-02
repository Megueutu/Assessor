from .financial.tools.balance import daily_balance, total_balance
from .financial.tools.transaction import add_transaction, search_transaction, update_transaction

from .faq import faq_retriever

FINANCIAL_TOOLS = [
    add_transaction,
    daily_balance,
    search_transaction,
    total_balance,
    update_transaction
]

FAQ_TOOLS = [
    faq_retriever
]
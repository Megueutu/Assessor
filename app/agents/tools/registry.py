from .financial.balance.daily_balance import daily_balance
from .financial.balance.total_balance import total_balance
from .financial.transaction.add_transaction import add_transaction
from .financial.transaction.search_transactions import search_transactions
from .financial.transaction.update_transaction import update_transaction
from .financial.transaction.purchase_wish import purchase_wish
from .faq.faq_retriever import faq_retriever
from .education.education_retriever import education_retriever
from .notes.note.add_note import add_note
from .notes.note.conclude_note import conclude_note
from .notes.note.list_notes import list_notes
from .notes.note.update_note import update_note
from .notes.note.add_note_item import add_note_item
from .notes.note.complete_note_item import complete_note_item
from .notes.wish.add_wish import add_wish
from .notes.wish.cancel_wish import cancel_wish
from .notes.wish.find_matching_wishes import find_matching_wishes
from .notes.wish.list_wishes import list_wishes
from .notes.wish.update_wish import update_wish
from .schedule.event.add_event import add_event
from .schedule.event.cancel_event import cancel_event
from .schedule.event.check_availability import check_availability
from .schedule.event.list_events import list_events
from .schedule.event.update_event import update_event

FINANCIAL_TOOLS = [
    daily_balance,
    total_balance,
    add_transaction,
    search_transactions,
    update_transaction,
    find_matching_wishes,
    purchase_wish,
]

FAQ_TOOLS = [
    faq_retriever,
]

EDUCATION_TOOLS = [
    education_retriever,
]

NOTES_TOOLS = [
    add_note,
    conclude_note,
    list_notes,
    update_note,
    add_note_item,
    complete_note_item,
    add_wish,
    list_wishes,
    update_wish,
    cancel_wish,
    find_matching_wishes,
]

SCHEDULE_TOOLS = [
    add_event,
    list_events,
    check_availability,
    update_event,
    cancel_event,
]

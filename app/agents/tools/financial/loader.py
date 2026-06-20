from json import loads
from pathlib import Path

_ALIASES_DIR = Path(__file__).resolve().parent / "aliases"

with open(_ALIASES_DIR / "category.json", "r", encoding="utf-8") as json_file:
    CATEGORY_ALIASES = loads(json_file.read())

with open(_ALIASES_DIR / "payment_method.json", "r", encoding="utf-8") as json_file:
    PAYMENT_METHOD_ALIASES = loads(json_file.read())
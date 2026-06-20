import json
from pathlib import Path


PII = [
    ("CPF",      r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}"),
    ("CNPJ",     r"\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}"),
    ("TELEFONE", r"\(?\d{2}\)?\s?\d{4,5}-?\d{4}"),
    ("EMAIL",    r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
    ("CONTA",    r"\d{4,6}-\d{1}"),
    ("CARTAO",   r"\d{4}\s?\d{4}\s?\d{4}\s?\d{4}"),
]


INJECTION_PATTERNS = [
    r"ignore\s+(as\s+)?instru[çc][oõ]es",
    r"ignore\s+previous\s+instructions",
    r"forget\s+your\s+instructions",
    r"you\s+are\s+now\s+",
    r"act\s+as\s+(if\s+)?",
    r"pretend\s+(you\s+are|to\s+be)",
    r"jailbreak",
    r"dan\s+mode",
    r"modo\s+irrestrito",
    r"system\s*prompt",
    r"<\s*system\s*>",
    r"\[INST\]",
    r"###\s*instruction",
    r"override\s+(your\s+)?instructions",
    r"desconsider[ea]\s+(suas\s+)?instru[çc][oõ]es",
]


_BLOCKLIST_PATH = Path(__file__).parent / "config" / "blocklist.json"
_blocklist = json.loads(_BLOCKLIST_PATH.read_text(encoding="utf-8"))

KEYWORDS_DADOS_INTERNOS = _blocklist["keywords_dados_internos"]

RESPOSTAS_BLOQUEIO = {
    categoria: (dados["motivo"], dados["mensagem"])
    for categoria, dados in _blocklist["respostas_bloqueio"].items()
}
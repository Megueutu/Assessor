import re

from app.core.llms import FAST_LLM as LLM
from app.agents.prompt.validator.compliance import COMPLIANCE_PROMPT
from app.agents.prompt.validator.classifier import CLASSIFIER_PROMPT
from app.workflow.guardrail.io import anonymize_input, deanonymize_output

from app.workflow.guardrail.constants import (
    PII,
    INJECTION_PATTERNS,
    KEYWORDS_INTERNAL_DATA,
    ANSWERS_FOR_BLOCK
)

def _block(reason, message): return {"bloqueado": True, "motivo": reason, "mensagem": message}
def _approved():             return {"bloqueado": False, "motivo": "aprovado", "mensagem": ""}
def _ok(conteudo):           return {"bloqueado": False, "motivo": "saida_revisada", "conteudo": conteudo}


def guardrail_in(anonymized_message):
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, anonymized_message, re.IGNORECASE):
            return _block("prompt_injection", "Não consigo processar essa solicitação.")

    texto_lower = anonymized_message.lower()
    for kw in KEYWORDS_INTERNAL_DATA:
        if kw in texto_lower:
            return _block("acesso_dados_internos", "Não tenho como compartilhar informações internas do sistema.")

    answer = LLM.invoke(CLASSIFIER_PROMPT.format(message=anonymized_message)).content

    category = "APROVADO"
    for linha in answer.splitlines():
        if linha.strip().upper().startswith("CATEGORIA:"):
            category = linha.split(":", 1)[1].strip().upper()
            break

    if category in ANSWERS_FOR_BLOCK:
        reason, message = ANSWERS_FOR_BLOCK[category]
        return _block(reason, message)

    return _approved()


def guardrail_out(answer, mapp, restore_pii=False):
    for tipo, padrao in PII: answer = re.sub(padrao, f"[{tipo} OMITIDO]", answer)
    answer = deanonymize_output(answer, mapp, restore=restore_pii)

    out = LLM.invoke(COMPLIANCE_PROMPT(answer)).content.strip()
    if "RESPOSTA:" in out:
        answer = out.split("RESPOSTA:", 1)[1].strip() or answer

    return _ok(answer)

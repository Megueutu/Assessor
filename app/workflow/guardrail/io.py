import uuid
import re
from app.workflow.guardrail.constants import PII


def anonymize_input(content: str):
    mapping = {}

    for pii_type, pattern in PII:
        matches = re.findall(pattern, content)

        for value in matches:
            token = f"[PII_{pii_type}_{uuid.uuid4().hex[:6]}]"
            mapping[token] = value
            content = content.replace(value, token, 1)

    return content, mapping


def deanonymize_output(content, mapping, restore=False):
    for token, value in mapping.items():
        if token in content:
            replacement = value if restore else f"[{token.split('_')[1]} OMITIDO]"

            content = content.replace(token, replacement)

    return content

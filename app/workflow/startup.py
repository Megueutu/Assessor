from dataclasses import dataclass
from typing import Callable

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

from app.core.config import config


@dataclass(frozen=True)
class ApiValidationResult:
    valid_groq_keys: int
    invalid_groq_keys: tuple[str, ...]
    gemini_valid: bool


def _test_groq_key(api_key: str) -> None:
    ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        groq_api_key=api_key,
        timeout=10,
        max_retries=0,
    ).invoke("Responda apenas OK.")


def _test_gemini_key(api_key: str) -> None:
    ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        google_api_key=api_key,
        request_timeout=10,
        retries=0,
    ).invoke("Responda apenas OK.")


def validate_api_keys(
    groq_probe: Callable[[str], None] = _test_groq_key,
    gemini_probe: Callable[[str], None] = _test_gemini_key,
) -> ApiValidationResult:
    """Valida credenciais antes da criação dos agentes e configura o pool Groq."""
    configured_groq_keys = config.GROQ_API_KEY_ENTRIES
    valid_groq_keys = []
    invalid_groq_keys = []
    for variable_name, api_key in configured_groq_keys:
        try:
            groq_probe(api_key)
            valid_groq_keys.append(api_key)
        except Exception:
            invalid_groq_keys.append(variable_name)

    gemini_valid = False
    if config.GEMINI_API_KEY:
        try:
            gemini_probe(config.GEMINI_API_KEY)
            gemini_valid = True
        except Exception:
            pass

    validation_errors = []
    if not valid_groq_keys:
        validation_errors.append("nenhuma chave Groq respondeu com sucesso")
    if not gemini_valid:
        validation_errors.append("GEMINI_API_KEY não respondeu com sucesso")
    if validation_errors:
        raise RuntimeError(f"Falha na validação de APIs: {'; '.join(validation_errors)}.")

    config.VALIDATED_GROQ_API_KEYS = valid_groq_keys
    return ApiValidationResult(
        valid_groq_keys=len(valid_groq_keys),
        invalid_groq_keys=tuple(invalid_groq_keys),
        gemini_valid=gemini_valid,
    )

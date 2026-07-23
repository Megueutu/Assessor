import os
import unittest

from dotenv import load_dotenv


load_dotenv()


def integration_tests_enabled() -> bool:
    return os.getenv("RUN_INTEGRATION_TESTS", "").lower() in {"1", "true", "yes"}


def workflow_tests_enabled() -> bool:
    return integration_tests_enabled() and os.getenv(
        "RUN_WORKFLOW_INTEGRATION_TESTS", ""
    ).lower() in {"1", "true", "yes"}


def require_environment(*names: str) -> dict[str, str]:
    values = {name: os.getenv(name, "").strip() for name in names}
    missing = [name for name, value in values.items() if not value]
    if missing:
        raise unittest.SkipTest(
            f"Configure as variáveis de integração: {', '.join(missing)}."
        )
    return values


def discover_api_keys(prefix: str) -> list[str]:
    entries = []
    for name, value in os.environ.items():
        if name == prefix:
            entries.append((0, value))
            continue
        numbered_prefix = f"{prefix}_"
        suffix = name.removeprefix(numbered_prefix)
        if name.startswith(numbered_prefix) and suffix.isdigit():
            entries.append((int(suffix) + 1, value))

    return [
        value
        for _, value in sorted(entries)
        if value
    ]

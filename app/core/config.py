import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    def __init__(self):
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        self.VALIDATED_GROQ_API_KEYS: list[str] | None = None

        self.POSTGRES_LOCAL = os.getenv("POSTGRES_LOCAL")
        self.MONGODB_LOCAL = os.getenv("MONGODB_LOCAL")

        self.POSTGRES_URI = os.getenv("POSTGRES_URI")
        self.POSTGRES_DB = os.getenv("POSTGRES_DB")
        self.POSTGRES_USER = os.getenv("POSTGRES_USER")
        self.POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

        self.MONGODB_URI = os.getenv("MONGODB_URI")
        self.MONGODB_DB = os.getenv("MONGODB_DB")

        self.FAQ_PDF_PATH = os.getenv("FAQ_PDF_PATH")
        self.TIMEZONE_REGION = os.getenv("TIMEZONE_REGION")

    @property
    def POSTGRES_DATABASE_URL(self) -> str | None:
        return self.POSTGRES_URI or self.POSTGRES_LOCAL

    @property
    def MONGODB_DATABASE_URL(self) -> str | None:
        return self.MONGODB_URI or self.MONGODB_LOCAL

    @property
    def GROQ_API_KEYS(self) -> list[str]:
        if self.VALIDATED_GROQ_API_KEYS is not None:
            return self.VALIDATED_GROQ_API_KEYS

        return [value for _, value in self.GROQ_API_KEY_ENTRIES]

    @property
    def GROQ_API_KEY_ENTRIES(self) -> list[tuple[str, str]]:
        entries = []
        known_values = set()

        for name, value in sorted(os.environ.items(), key=_groq_key_order):
            if _is_groq_key_name(name) and value and value not in known_values:
                entries.append((name, value))
                known_values.add(value)
        return entries


def _is_groq_key_name(name: str) -> bool:
    if name == "GROQ_API_KEY":
        return True
    prefix = "GROQ_API_KEY_"
    return name.startswith(prefix) and name[len(prefix):].isdigit()


def _groq_key_order(item: tuple[str, str]) -> tuple[int, int]:
    name = item[0]
    if name == "GROQ_API_KEY":
        return (0, 0)
    if _is_groq_key_name(name):
        return (0, int(name.removeprefix("GROQ_API_KEY_")) + 1)
    return (1, 0)


config = Config()

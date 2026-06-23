import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    def __init__(self):
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")

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


config = Config()
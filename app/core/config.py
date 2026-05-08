import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.GEMINI_API_KEY     = os.getenv("GEMINI_API_KEY")
        self.GROQ_API_KEY       = os.getenv("GROQ_API_KEY")
        self.PSQL_DATABASE_URL  = os.getenv("PSQL_DATABASE_URL")
        self.MONGO_DATABASE_URL = os.getenv("MONGO_DATABASE_URL")
        self.FAQ_PDF_PATH       = os.getenv("FAQ_PDF_PATH")
        self.TIMEZONE_REGION    = os.getenv("TIMEZONE_REGION")

config = Config()
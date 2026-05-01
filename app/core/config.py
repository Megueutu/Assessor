import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.GROQ_API_KEY   = os.getenv("GROQ_API_KEY")
        self.DATABASE_URL   = os.getenv("DATABASE_URL")
        self.FAQ_PDF_PATH   = os.getenv("FAQ_PDF_PATH")

config = Config()
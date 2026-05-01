import os

from dotenv import load_dotenv
from langchain.tools import tool
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS  # pip install faiss-cpu
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

PDF_PATH = os.getenv("FAQ_PDF_PATH", "faq.pdf")

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-2-preview",
    google_api_key=os.getenv("GEMINI_API_KEY"),
)


@tool
def faq_retriever(query: str) -> str:
    """Busca informações no documento FAQ com base na pergunta do usuário."""
    loader = PyPDFLoader(PDF_PATH)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=150)
    chunks = splitter.split_documents(docs)

    db = FAISS.from_documents(chunks, embeddings)
    results = db.similarity_search(
        query, k=6
    )  # k=quantidade de chunks mais relevantes a retornar

    return "\n\n".join(
        [result.page_content for result in results]
    )  # Basicamente, retorna o conteúdo dos 6 chunks mais relevantes encontrados no PDF

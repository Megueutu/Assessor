from app.core.config import config
from app.core.llms   import EMBEDDING_MODEL

from langchain.tools import tool
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores     import FAISS


loader = PyPDFLoader(config.FAQ_PDF_PATH)
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=150)
chunks = splitter.split_documents(docs)

db = FAISS.from_documents(chunks, EMBEDDING_MODEL)

@tool("faq_retriever")
def faq_retriever(query: str) -> str:
    """Busca informações no documento FAQ com base na pergunta do usuário."""
    
    results = db.similarity_search(query, k=6)
    return "\n\n".join([result.page_content for result in results])

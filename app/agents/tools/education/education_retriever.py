from pathlib import Path
from threading import Lock

from langchain.tools import tool
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.agents.tools.education.document_registry import discover_documents, load_documents
from app.agents.tools.response import ToolResponse
from app.core.config import config


_CHUNK_SIZE = 700
_CHUNK_OVERLAP = 150
_RESULT_LIMIT = 6

_INDEX_LOCK = Lock()
_INDEX = None
_INDEX_SIGNATURE = ()


def _corpus_signature(paths: list[Path]) -> tuple:
    return tuple(
        (str(path.resolve()), path.stat().st_mtime_ns, path.stat().st_size)
        for path in paths
    )


def _build_index(chunks):
    from app.core.llms import EMBEDDING_MODEL

    return FAISS.from_documents(chunks, EMBEDDING_MODEL)


def _get_index():
    global _INDEX, _INDEX_SIGNATURE

    paths = discover_documents(config.EDUCATION_DOCUMENTS_PATH)
    signature = _corpus_signature(paths)

    if not paths:
        return None
    if _INDEX is not None and signature == _INDEX_SIGNATURE:
        return _INDEX

    with _INDEX_LOCK:
        paths = discover_documents(config.EDUCATION_DOCUMENTS_PATH)
        signature = _corpus_signature(paths)

        if not paths:
            return None
        if _INDEX is not None and signature == _INDEX_SIGNATURE:
            return _INDEX

        documents = load_documents(config.EDUCATION_DOCUMENTS_PATH)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=_CHUNK_SIZE,
            chunk_overlap=_CHUNK_OVERLAP,
        )
        chunks = splitter.split_documents(documents)

        if not chunks:
            return None

        _INDEX = _build_index(chunks)
        _INDEX_SIGNATURE = signature
        return _INDEX


@tool("education_retriever")
def education_retriever(query: str) -> dict:
    """Busca conteúdo nos materiais internos de educação financeira."""
    try:
        index = _get_index()
        if index is None:
            return ToolResponse.error(
                message="Nenhum material de educação financeira está disponível."
            )

        results = index.similarity_search(query, k=_RESULT_LIMIT)
        return ToolResponse.ok(
            results=[
                {
                    "content": result.page_content,
                    "source": result.metadata.get("source"),
                    "file_name": result.metadata.get("file_name"),
                    "page": result.metadata.get("page_number"),
                }
                for result in results
            ],
            total=len(results),
        )
    except Exception:
        return ToolResponse.error(
            message="Não foi possível consultar os materiais de educação financeira."
        )

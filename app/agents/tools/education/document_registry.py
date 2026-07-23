from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document


DOCUMENT_LOADERS = {
    ".md": lambda path: TextLoader(str(path), encoding="utf-8"),
    ".pdf": lambda path: PyPDFLoader(str(path)),
}


def discover_documents(documents_path: str | Path) -> list[Path]:
    root = Path(documents_path)
    if not root.is_dir():
        return []

    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in DOCUMENT_LOADERS
    )


def load_documents(documents_path: str | Path) -> list[Document]:
    root = Path(documents_path)
    documents = []

    for path in discover_documents(root):
        loader = DOCUMENT_LOADERS[path.suffix.lower()](path)

        for document in loader.load():
            page = document.metadata.get("page")
            document.metadata.update({
                "source": path.relative_to(root).as_posix(),
                "file_name": path.name,
                "document_type": path.suffix.lower().removeprefix("."),
                "page_number": page + 1 if isinstance(page, int) else None,
            })
            documents.append(document)

    return documents

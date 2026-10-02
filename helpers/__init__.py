"""Helpers for extracting, preparing, and chunking the homework books."""

from .chunking import chunk_markdown
from .extract import extract_pdf_text, write_pdf_directory, write_pdf_text
from .index_docs import build_index, index_chunks, load_chunks, prepare_documents, search
from .prepare import prepare_directory, prepare_markdown
from .models import RAGResponse
from .rag import build_prompt, llm, llm_chat, new_messages, rag

__all__ = [
    "build_index",
    "chunk_markdown",
    "extract_pdf_text",
    "index_chunks",
    "search",
    "load_chunks",
    "prepare_directory",
    "prepare_documents",
    "build_prompt",
    "llm",
    "llm_chat",
    "new_messages",
    "RAGResponse",
    "prepare_markdown",
    "rag",
    "write_pdf_directory",
    "write_pdf_text",
]

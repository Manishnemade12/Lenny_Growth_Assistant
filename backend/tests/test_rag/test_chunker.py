"""Unit tests for RAG text chunking and embedding logic."""

from app.rag.chunker import RecursiveCharacterChunker
from app.rag.embeddings import EmbeddingService


def test_chunker_basic_split():
    chunker = RecursiveCharacterChunker(chunk_size=100, chunk_overlap=10)
    text = "Hello world! " * 20
    chunks = chunker.split(text)
    assert len(chunks) > 1
    assert all(len(c) <= 120 for c in chunks)


def test_chunker_empty_input():
    chunker = RecursiveCharacterChunker(chunk_size=100, chunk_overlap=10)
    assert chunker.split("") == []


def test_fallback_embedding_dimension():
    service = EmbeddingService()
    vector = service._generate_fallback_embedding("test text")
    assert len(vector) == service.dimension
    assert isinstance(vector[0], float)

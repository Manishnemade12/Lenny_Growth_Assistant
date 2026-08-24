"""Recursive character text chunker for splitting transcripts into overlapping segments.

Follows TDD.md Section 4.2 specifications: 500 token chunks with 50 token overlap.
"""

import re


class RecursiveCharacterChunker:
    """Splits text recursively using hierarchical separators with overlap."""

    SEPARATORS = ["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " "]

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, text: str) -> list[str]:
        """Clean and split text into overlapping chunks."""
        cleaned_text = self._clean_text(text)
        if not cleaned_text:
            return []

        raw_chunks = self._recursive_split(cleaned_text, self.SEPARATORS)
        return self._add_overlap(raw_chunks)

    def _clean_text(self, text: str) -> str:
        """Normalize whitespace and clean up markdown artifacts."""
        text = re.sub(r"\r\n", "\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _recursive_split(self, text: str, separators: list[str]) -> list[str]:
        """Recursively break text down by separator hierarchy."""
        if len(text) <= self.chunk_size:
            return [text] if text.strip() else []

        chunks: list[str] = []
        current_sep = separators[0] if separators else ""
        remaining_seps = separators[1:] if len(separators) > 1 else []

        parts = text.split(current_sep) if current_sep else [text]
        current_chunk = ""

        for part in parts:
            test_chunk = f"{current_chunk}{current_sep}{part}" if current_chunk else part

            if len(test_chunk) <= self.chunk_size:
                current_chunk = test_chunk
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())

                if len(part) > self.chunk_size and remaining_seps:
                    sub_chunks = self._recursive_split(part, remaining_seps)
                    chunks.extend(sub_chunks)
                    current_chunk = ""
                else:
                    current_chunk = part

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    def _add_overlap(self, chunks: list[str]) -> list[str]:
        """Add overlap context between consecutive chunks."""
        if len(chunks) <= 1 or self.chunk_overlap <= 0:
            return chunks

        overlapped: list[str] = [chunks[0]]
        for i in range(1, len(chunks)):
            prev_tail = chunks[i - 1][-self.chunk_overlap:]
            overlapped.append(f"{prev_tail} {chunks[i]}")

        return overlapped

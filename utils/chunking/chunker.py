from __future__ import annotations
from .config import CHUNK_SIZE, OVERLAP

"""
Chunking logic for doc ingestion.

How it flows:

1. Document metadata is loaded from `manifest.json` 
2. Text is extracted form the source file intoo per-page data
3. Pages are split into overlapping chunks for downstream ingestion

This module handles step (3): converting extracted page data
into normalized text chunks with metadata
"""

def chunk_page(page_data: dict, doc_id: str, source_file: str) -> list[dict]:
    pass

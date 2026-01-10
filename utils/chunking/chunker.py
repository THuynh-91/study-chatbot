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

# Chunks a single page
def chunk_page(page_data: dict, doc_id: str, source_file: str) -> list[dict]:
    
    # Calls the extractor and the extractor is a list[dict] 
    text = page_data["text"]
    page_num = page_data.get("page") or page_data.get("slide")

    # Refer to the config, may need to adjust CHUNK_SIZE while testing
    
    # If text fits in one chunk, return as is
    # The metadata is for debugging, knowing where the chunk cam from
    if len(text) <= CHUNK_SIZE:
        return [{
            "text": text,
            "metadata": {
                "doc_id"      : doc_id,
                "source_file" : source_file,
                "page"        : page_num,
                "chunk_index" : 0,
                "chunk_type"  : "full_page"
            }
        }]

    chunks = []
    start = 0
    chunk_index = 0

    while start < len(text):
        # Extract a chunk
        end = start + CHUNK_SIZE
        chunk_text = text[start:end]

        # Add to list
        chunks.append({
            "text": chunk_text,
            "metadata": {
                "doc_id"      : doc_id,
                "source_file" : source_file,
                "page"        : page_num,
                "chunk_index" : chunk_index,
                "chunk_type"  : "split_page"
            }
        })

        # Update our new start, also take into consideration the overlap
        start += (CHUNK_SIZE - OVERLAP)
        chunk_index += 1

    return chunks


# Creates chunks from ALL pages (calls chunk_page) 
def create_chunks(pages_data: list[dict], doc_id: str, source_file: str) -> list[dict]:
    all_chunks = []

    for page_data in pages_data:
        page_chunks = chunk_page(page_data, doc_id, source_file)
        all_chunks.extend(page_chunks)

    return all_chunks
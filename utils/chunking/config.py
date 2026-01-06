"""
Chunking configuration for document ingestion.

Design goals:
- Preserve semantic coherence within each chunk
- Maintain sufficient overlap to avoid context loss
- Prevent pathological chunk sizes from malformed inputs

These defaults are tuned for LLM ingestion pipelines and
can be adjusted based on downstream context window limits.

Reasoning for configs: (still WIP and need testing)

Most of files will be in PDFs of typically (5-20) pages,
the input PPTX will be at typically ~50 slides maximum. When
conforming to these inputs we realize that we aren't chunking 
thousands of pdf files and pages at a large scale, and 
can increase the context size for better accuracy and not
sacrifice much speed and efficieny. Will need to adapt IF
I do decide to upload textbooks.
"""

# Chunking configuration
CHUNK_SIZE = 1000  # Maximum characters per chunk
OVERLAP = 150      # Character overlap between chunks
MAX_CHUNK_SIZE = 1500  # Hard limit

# Supported file types
SUPPORTED_TEXT_FILES = [".txt", ".md"]
SUPPORTED_PDF_FILES = [".pdf"]
SUPPORTED_PPTX_FILES = [".pptx"]




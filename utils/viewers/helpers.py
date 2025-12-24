from __future__ import annotations
from pathlib import Path


def cache_key_from_upload(file_path: Path) -> str:
    """
    stored_name format: {doc_id}__{original_name}
    Use doc_id as cache key to avoid collisions.
    """
    name = file_path.name
    if "__" in name:
        return name.split("__", 1)[0]
    return file_path.stem


def safe_mtime_int(p: Path) -> int:
    try:
        return int(p.stat().st_mtime)
    except Exception:
        return 0

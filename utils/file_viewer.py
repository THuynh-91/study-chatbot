from __future__ import annotations
from pathlib import Path
import streamlit as st
from .viewers import view_pdf, view_pptx, view_image, view_video, view_text


def view_file(file_path: Path, original_name: str | None = None):
    """
    Main router for file viewing.
    Delegates to appropriate viewer based on file extension.
    """
    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        view_pdf(file_path)
    elif suffix == ".pptx":
        view_pptx(file_path)
    elif suffix in [".mp4", ".mov", ".avi", ".mkv", ".webm"]:
        view_video(file_path)
    elif suffix in [".txt", ".md", ".csv", ".json", ".py", ".js", ".html", ".css", ".xml"]:
        view_text(file_path)
    elif suffix in [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".webp"]:
        view_image(file_path)
    else:
        st.warning(f"Preview not available for {suffix} files.")
        st.info("Download the file to view it.")

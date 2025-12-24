from __future__ import annotations
from pathlib import Path
import streamlit as st
from .config import VIEWER_HEIGHT


def view_text(file_path: Path):
    try:
        content = file_path.read_text(encoding="utf-8")
        st.text_area("File Content", content, height=VIEWER_HEIGHT, disabled=True)
    except UnicodeDecodeError:
        st.error("Cannot display file — not a valid text file.")
    except Exception as e:
        st.error(f"Error reading file: {e}")

from __future__ import annotations
import base64
from pathlib import Path
import streamlit as st
from .config import VIEWER_HEIGHT
from .helpers import safe_mtime_int


@st.cache_data(show_spinner=False)
def _image_b64_cached(path_str: str, mtime: int) -> str:
    data = Path(path_str).read_bytes()
    return base64.b64encode(data).decode("utf-8")


def view_image(file_path: Path):
    if not file_path.exists():
        st.error(f"File not found: {file_path}")
        return

    try:
        mtime = safe_mtime_int(file_path)
        b64 = _image_b64_cached(str(file_path), mtime)

        st.markdown(
            f"""
            <div style="
                height:{VIEWER_HEIGHT}px;
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 12px;
                padding: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                overflow: hidden;
                background: rgba(255,255,255,0.02);
            ">
              <img
                src="data:image/*;base64,{b64}"
                style="max-width:100%; max-height:100%; object-fit:contain;"
              />
            </div>
            """,
            unsafe_allow_html=True,
        )
    except Exception as e:
        st.error(f"Error displaying image: {e}")

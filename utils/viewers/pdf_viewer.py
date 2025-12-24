from __future__ import annotations
import base64
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
from .config import VIEWER_HEIGHT, DEFAULT_PAGES
from .helpers import cache_key_from_upload, safe_mtime_int


def _count_pdf_pages(pdf_path: Path) -> int | None:
    try:
        import fitz  # PyMuPDF

        d = fitz.open(str(pdf_path))
        n = len(d)
        d.close()
        return n
    except Exception:
        return None


def _render_pdf_pages_as_images(pdf_path: Path, cache_key: str, pages_to_render: int, zoom: float = 2.0):
    import fitz  # PyMuPDF

    total = _count_pdf_pages(pdf_path)
    if total is None:
        st.error("Could not read PDF.")
        return

    pages_to_render = max(1, min(int(pages_to_render), total))
    pdf_mtime = safe_mtime_int(pdf_path)

    cache_dir = pdf_path.parent / "_pdf_png_cache" / cache_key
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Build HTML that contains all images INSIDE a single scroll box
    html_parts = [
        f"""
        <div style="
            height: {VIEWER_HEIGHT}px;
            overflow-y: auto;
            border: 1px solid rgba(255,255,255,0.15);
            border-radius: 12px;
            padding: 12px;
            background: rgba(255,255,255,0.02);
        ">
        """
    ]

    doc = fitz.open(str(pdf_path))

    for i in range(pages_to_render):
        png_path = cache_dir / f"p{i+1:04d}_z{int(zoom*100)}.png"

        needs = True
        if png_path.exists():
            try:
                needs = int(png_path.stat().st_mtime) < pdf_mtime
            except Exception:
                needs = True

        if needs:
            page = doc[i]
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            png_path.write_bytes(pix.tobytes("png"))

        # Embed image as base64 INSIDE the HTML scroll box
        b64 = base64.b64encode(png_path.read_bytes()).decode("utf-8")
        html_parts.append(
            f"""
            <div style="margin-bottom: 14px;">
              <img src="data:image/png;base64,{b64}" style="width:100%; border-radius:10px;" />
            </div>
            """
        )

    doc.close()

    html_parts.append("</div>")
    html = "\n".join(html_parts)

    # Render as one component so the scroll box actually contains the images
    components.html(html, height=VIEWER_HEIGHT + 24, scrolling=False)

    st.caption(f"Showing {pages_to_render} / {total} page(s)")


def view_pdf(file_path: Path):
    if not file_path.exists():
        st.error(f"File not found: {file_path}")
        return

    cache_key = cache_key_from_upload(file_path)
    total = _count_pdf_pages(file_path)

    if total is None:
        st.error("Could not read PDF (install PyMuPDF: pip install pymupdf).")
        return

    default_load = min(DEFAULT_PAGES, total)

    if total > DEFAULT_PAGES:
        pages_to_load = st.number_input(
            "How many pages should I load?",
            min_value=1,
            max_value=total,
            value=default_load,
            step=1,
            key=f"pdf_pages_to_load_{cache_key}",
        )
    else:
        pages_to_load = default_load

    st.caption(f"PDF: {total} page(s). Rendering first {int(pages_to_load)}…")
    _render_pdf_pages_as_images(file_path, cache_key=cache_key, pages_to_render=int(pages_to_load), zoom=2.0)

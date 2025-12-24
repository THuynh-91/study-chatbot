from __future__ import annotations
import shutil
import subprocess
from pathlib import Path
import streamlit as st
from .config import DEFAULT_PAGES
from .helpers import cache_key_from_upload
from .pdf_viewer import _count_pdf_pages, _render_pdf_pages_as_images


def _find_soffice() -> str | None:
    found = shutil.which("soffice")
    if found:
        return found

    candidates = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    return None


def _convert_pptx_to_pdf_cached(pptx_path: Path) -> Path:
    if not pptx_path.exists():
        raise FileNotFoundError(f"PPTX not found: {pptx_path}")

    soffice_cmd = _find_soffice()
    if not soffice_cmd:
        raise FileNotFoundError(
            "LibreOffice not found (soffice.exe). Install LibreOffice or add it to PATH."
        )

    cache_key = cache_key_from_upload(pptx_path)
    cache_dir = pptx_path.parent / "_pptx_pdf_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = cache_dir / f"{cache_key}.pdf"

    # Reuse cached PDF if up-to-date
    if pdf_path.exists():
        try:
            if pdf_path.stat().st_mtime >= pptx_path.stat().st_mtime:
                return pdf_path
        except OSError:
            pass

    cmd = [
        soffice_cmd,
        "--headless",
        "--nologo",
        "--nofirststartwizard",
        "--convert-to",
        "pdf",
        "--outdir",
        str(cache_dir),
        str(pptx_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            "LibreOffice conversion failed.\n\n"
            f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
        )

    # LibreOffice outputs {stem}.pdf; rename to stable cache key if needed
    lo_pdf = cache_dir / f"{pptx_path.stem}.pdf"
    if lo_pdf.exists() and lo_pdf != pdf_path:
        try:
            if pdf_path.exists():
                pdf_path.unlink()
        except OSError:
            pass
        lo_pdf.rename(pdf_path)

    if not pdf_path.exists():
        pdfs = list(cache_dir.glob("*.pdf"))
        if len(pdfs) == 1:
            return pdfs[0]
        raise RuntimeError("Conversion reported success but cached PDF was not found.")

    return pdf_path


def view_pptx(file_path: Path):
    try:
        if not file_path.exists():
            st.error(f"File not found: {file_path}")
            return

        cache_key = cache_key_from_upload(file_path)
        full_pdf = _convert_pptx_to_pdf_cached(file_path)
        total = _count_pdf_pages(full_pdf)

        if total is None:
            st.error("Converted to PDF, but PyMuPDF couldn't read it. (pip install pymupdf)")
            return

        default_load = min(DEFAULT_PAGES, total)

        if total > DEFAULT_PAGES:
            pages_to_load = st.number_input(
                "How many slides should I load?",
                min_value=1,
                max_value=total,
                value=default_load,
                step=1,
                key=f"pptx_pages_to_load_{cache_key}",
            )
        else:
            pages_to_load = default_load

        st.caption(f"Deck: {total} slide(s). Rendering first {int(pages_to_load)}…")
        _render_pdf_pages_as_images(full_pdf, cache_key=cache_key, pages_to_render=int(pages_to_load), zoom=2.0)

    except FileNotFoundError as e:
        st.error(str(e))
        st.info(
            "LibreOffice is required on the machine running Streamlit (not the user).\n"
            r"Typical Windows path: C:\Program Files\LibreOffice\program\soffice.exe"
        )
    except Exception as e:
        st.error(f"Error previewing PPTX: {e}")

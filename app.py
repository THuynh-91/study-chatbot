import streamlit as st
import PyPDF2
from io import BytesIO
import base64
import time
from pathlib import Path
import json, uuid
from datetime import datetime, timezone


def project_dirs(project_id: str):
    base = Path("data") / "projects" / project_id

     # Points UPLOAD_DIR -> data/uploads
    upload_dir = base / "uploads"
    manifest_path = base / "manifest.json"

    # Makes the dir if it doesn't exist
    upload_dir.mkdir(parents=True, exist_ok=True)

    return upload_dir, manifest_path

def load_manifest(manifest_path: Path):
    if manifest_path.exists():
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    return []

def save_manifest(manifest_path: Path, manifest: list[dict]):
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()

def short_ts(iso_str: str) -> str:
    if not iso_str:
        return ""
    return iso_str.replace("T", " ")[:16]


def human_kb(nbytes: int) -> str:
    return f"{nbytes/1024:.1f} KB" if nbytes < 1024*1024 else f"{nbytes/1024/1024:.2f} MB"


def initialize_session_state():
    # Initializing the current page
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Chat'

    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []

    if 'rag_uploader_key' not in st.session_state:
        st.session_state.rag_uploader_key = 0

    if "selected_doc_ids" not in st.session_state:
        st.session_state.selected_doc_ids = set()

    if "sort_mode" not in st.session_state:
        st.session_state.sort_mode = "Newest"

def render_sidebar():
    # Sidebar 
    with st.sidebar:
        st.title("Navigation")

        if st.button("New Chat", use_container_width = True):
            st.session_state.current_page = "Chat"

        if st.button("File Manager", use_container_width = True):
            st.session_state.current_page = "File Manager"

# Renders the chatpage... dunno if this will include new and old chats?
def render_chat_page():
    if st.session_state.current_page == "Chat":
        st.title("Chat")
        st.info("Chat page - WIP")

def render_file_manager_page():

    
    # Hides upload icon & reduces spacing from header & markdown
    st.markdown("""
    <style>
    /* Pull everything to the top */
    .block-container {
        padding-top: 2.75rem !important;
    }

    /* Optional: remove extra top margin on the header itself */
    h2 {
        margin-top: 0rem !important;
        margin-bottom: -1.5rem !important;
    }

    /* Only hide upload icon */
    [data-testid="stFileUploader"] section svg {
        display: none;
    }       

    /* Hides the output files that are uploaded */   
    [data-testid="stFileUploaderFile"] {
        display: none;}
                
    /* Hides the page output files */
    [data-testid="stFileUploaderPagination"] {
        display: none;}


    /* Center checkboxes only when they're inside a column (not standalone elements) */
    [data-testid="stHorizontalBlock"] div[data-testid="stVerticalBlock"]:has(.stCheckbox) {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }

    [data-testid="stHorizontalBlock"] div[data-testid="stVerticalBlock"]:has(.stCheckbox) > * {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }

    </style>
    """, unsafe_allow_html=True)

    project_id = "default"
    UPLOAD_DIR, MANIFEST_PATH = project_dirs(project_id)
    manifest = load_manifest(MANIFEST_PATH)


    # Two columns, title and then uploader
    col1, col2 = st.columns([4, 1.5])

    with col1:
        st.header("File Manager")
        st.markdown("Upload and manage your RAG knowledge base")

    with col2:
        st.write("")
        
        #File uploader 
        uploaded_files = st.file_uploader(
            label = 'Upload Files for RAG',
            label_visibility = 'collapsed',
            accept_multiple_files = True,
            type = None,
            width = 405,
            key = f"rag_uploader_{st.session_state.rag_uploader_key}"
        )


    if uploaded_files:
        for f in uploaded_files:
            '''
            File = "notes.pdf

            f.name = 'notes.pdf'
            f.getvalue() -- actual contents of notes.pdf

            This is then saved:
            save_path -- builds the full file path (data/uploads/notes.pdf)
            save_path.write_bytes -- creates or overwrites the file
            '''
            original_name = f.name
            file_bytes = f.getvalue()
            doc_id = str(uuid.uuid4())

            stored_name = f"{doc_id}__{original_name}"
            (UPLOAD_DIR / stored_name).write_bytes(file_bytes)

            manifest.append({
                "doc_id": doc_id,
                "original_name": original_name,
                "stored_name": stored_name,
                "bytes": len(file_bytes),
                "uploaded_at": utc_now_iso()
            })

        save_manifest(MANIFEST_PATH, manifest)
        
        # clear uploader so nothing is stored
        '''
        Streamlit widget remembers states via key:
        By changing the key we destroy the old uploader
            and also create a brand-new empty uploader
            making the uploader temporary and doesn't store anything.
        '''
        st.session_state.rag_uploader_key += 1
        st.rerun()

    # Divider
    st.markdown("""
        <hr style="margin-top: -1rem; margin-bottom: 1rem; width: 100%">
    """, unsafe_allow_html=True)

    t1, t2, t3, t4 = st.columns([2.2, 1.1, 1.3, 1.2], vertical_alignment="center")

    # Filter
    with t1:
        sort_mode = st.selectbox(
            "Sort",
            ["Newest", "Oldest", "Name (A→Z)", "Name (Z→A)", "Size (Smallest)", "Size (Largest)"],
            key="sort_mode",
            label_visibility="collapsed",
        )

    # Select all docs
    with t2:
        if st.button("Select all", use_container_width=True):
            st.session_state.selected_doc_ids = {m["doc_id"] for m in manifest}
            st.rerun()

    # Deselect all docs
    with t3:
        if st.button("Deselect all", use_container_width=True):
            st.session_state.selected_doc_ids = set()
            st.rerun()

    #TBD
    with t4:
        # Placeholder behavior for now: "Apply" just confirms draft is saved.
        # Later you'll compare draft vs applied and show the popup diff.
        apply_clicked = st.button("Apply", use_container_width=True, type="primary")

    def sort_key(item: dict):
            if sort_mode in ("Newest", "Oldest"):
                return item.get("uploaded_at", "")
            
            if sort_mode in ("Name (A→Z)", "Name (Z→A)"):
                return item.get("original_name", "").lower()
            
            if sort_mode in ("Size (Largest)", "Size (Smallest)"):
                return item.get("bytes", 0)
            
            return item.get("uploaded_at", "")
        
        
    reverse = sort_mode in ("Newest", "Name (Z→A)", "Size (Largest)")
    
    manifest_view = sorted(manifest, key=sort_key, reverse=reverse)
    st.caption(f"Selected documents: {len(st.session_state.selected_doc_ids)}")

    if not manifest_view:
        st.info("No files uploaded yet.")
    else:
        for item in manifest_view:
            doc_id = item["doc_id"]
            name = item["original_name"]
            size = human_kb(item["bytes"])
            ts = item["uploaded_at"]

            # default: newly uploaded files are selected
            if doc_id not in st.session_state.selected_doc_ids:
                st.session_state.selected_doc_ids.add(doc_id)

            c1, c2, c3 = st.columns([0.8, 6, 1.2], vertical_alignment="center")

            # ---- Checkbox (draft selection) ----
            with c1:
                checked = st.checkbox(
                    "",
                    value=(doc_id in st.session_state.selected_doc_ids),
                    key=f"use_{doc_id}",
                )

                if checked:
                    st.session_state.selected_doc_ids.add(doc_id)
                else:
                    st.session_state.selected_doc_ids.discard(doc_id)

            # Filename + metadata 
            with c2:
                ts_short = short_ts(ts)
                st.markdown(
                    f"""
                    <span style="font-weight:600;">{name}</span>
                    <span style="opacity:0.65; font-size:0.85rem;">
                        &nbsp;·&nbsp;{size}&nbsp;·&nbsp;{ts_short}
                    </span>

                    """,
                    unsafe_allow_html=True,
                )


            # Delete (disabled if selected) 
            with c3:
                delete_disabled = doc_id in st.session_state.selected_doc_ids

                if st.button(
                    "Delete",
                    key=f"del_{doc_id}",
                    use_container_width=True,
                    disabled=delete_disabled,
                ):
                    # delete file from disk
                    file_path = UPLOAD_DIR / item["stored_name"]
                    if file_path.exists():
                        file_path.unlink()

                    # remove from manifest
                    manifest = [m for m in manifest if m["doc_id"] != doc_id]
                    save_manifest(MANIFEST_PATH, manifest)

                    # remove from draft selection
                    st.session_state.selected_doc_ids.discard(doc_id)

                    st.rerun()


def main():
    # Page config
    st.set_page_config(
        page_title="Study Chatbot",
        page_icon="🎓",
        layout="wide"
    )

    initialize_session_state()

    render_sidebar()

    if st.session_state.current_page == "Chat":
        render_chat_page()

    elif st.session_state.current_page == "File Manager":
        render_file_manager_page()

if __name__ == "__main__":
    main()
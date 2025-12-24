import streamlit as st
import uuid
from utils.file_helpers import (
    project_dirs,
    load_manifest,
    save_manifest,
    utc_now_iso,
    short_ts,
    human_kb
)


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

            # IMPORTANT: update widget state for each checkbox key
            for m in manifest:
                st.session_state[f"use_{m['doc_id']}"] = True

            st.rerun()

    # Deselect all docs
    with t3:
        if st.button("Deselect all", use_container_width=True):
            st.session_state.selected_doc_ids = set()

            for m in manifest:
                st.session_state[f"use_{m['doc_id']}"] = False
            
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

    count_slot = st.empty()   # placeholder for the caption
    count_slot.caption(f"Selected documents: {len(st.session_state.selected_doc_ids)}")

    manifest_view = sorted(manifest, key=sort_key, reverse=reverse)

    if not manifest_view:
        st.info("No files uploaded yet.")
    else:
        for item in manifest_view:
            doc_id = item["doc_id"]
            name = item["original_name"]
            size = human_kb(item["bytes"])
            ts = item["uploaded_at"]

            c1, c2, c3 = st.columns([0.8, 6, 1.2], vertical_alignment="center")

            # ---- Checkbox (draft selection) ----
            with c1:
                # Check current state before rendering
                was_selected = doc_id in st.session_state.selected_doc_ids

                # Render checkbox with current state
                is_checked = st.checkbox(
                    "",
                    value=was_selected,
                    key=f"use_{doc_id}",
                )

                # Update session state based on checkbox interaction
                if is_checked != was_selected:
                    if is_checked:
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
    
    new_selected = set()
    for m in manifest:
        doc_id = m["doc_id"]
        if st.session_state.get(f"use_{doc_id}", False):
            new_selected.add(doc_id)

    st.session_state.selected_doc_ids = new_selected
    count_slot.caption(f"Selected documents: {len(new_selected)}")

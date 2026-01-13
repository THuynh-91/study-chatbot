import streamlit as st
import uuid
from utils.file_helpers import (
    project_dirs,
    load_manifest,
    save_manifest,
    utc_now_iso,
    short_ts,
    human_kb,
    load_selections,
    save_selections
)
from utils.file_viewer import view_file
from utils.chunking import extract_text, create_chunks, store_chunks, delete_document_chunks 



def render_file_manager_page():

    st.markdown("""
    <style>
    .block-container { padding-top: 2.75rem !important; }

    h2 {
        margin-top: 0rem !important;
        margin-bottom: -1.5rem !important;
    }

    [data-testid="stFileUploader"] section svg { display: none; }
    [data-testid="stFileUploaderFile"] { display: none; }
    [data-testid="stFileUploaderPagination"] { display: none; }

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

    # Load persisted selections on first load
    if "selected_doc_ids" not in st.session_state:
        st.session_state.selected_doc_ids = load_selections(project_id)

    # Sync checkbox widget states with selected_doc_ids on page load
    for item in manifest:
        doc_id = item["doc_id"]
        checkbox_key = f"use_{doc_id}"
        # If checkbox key doesn't exist yet, initialize it from selected_doc_ids
        if checkbox_key not in st.session_state:
            st.session_state[checkbox_key] = doc_id in st.session_state.selected_doc_ids

    # Two columns, title and then uploader
    col1, col2 = st.columns([4, 1.5])

    with col1:
        st.header("File Manager")
        st.markdown("Upload and manage your RAG knowledge base")

    with col2:
        st.write("")
        uploaded_files = st.file_uploader(
            label='Upload Files for RAG',
            label_visibility='collapsed',
            accept_multiple_files=True,
            type=None,
            width=405,
            key=f"rag_uploader_{st.session_state.rag_uploader_key}"
        )

    if uploaded_files:
        for f in uploaded_files:
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

        st.session_state.rag_uploader_key += 1
        st.rerun()

    # Divider
    st.markdown("""<hr style="margin-top: -1rem; margin-bottom: 1rem; width: 100%">""",
                unsafe_allow_html=True)

    t1, t2, t3, t4 = st.columns([2.2, 1.1, 1.3, 1.2], vertical_alignment="center")

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
            for m in manifest:
                st.session_state[f"use_{m['doc_id']}"] = True
            # Close viewer when selecting all
            st.session_state.viewer_open = False
            st.session_state.viewer_doc_id = None
            # Persist selections to disk
            save_selections(project_id, st.session_state.selected_doc_ids)
            st.rerun()

    # Deselect all docs
    with t3:
        if st.button("Deselect all", use_container_width=True):
            st.session_state.selected_doc_ids = set()
            for m in manifest:
                st.session_state[f"use_{m['doc_id']}"] = False
            # Close viewer when deselecting all
            st.session_state.viewer_open = False
            st.session_state.viewer_doc_id = None
            # Persist selections to disk
            save_selections(project_id, st.session_state.selected_doc_ids)
            st.rerun()

        with t4:
            apply_clicked = st.button("Apply", use_container_width=True, type="primary")
        
        if apply_clicked:
            if not st.session_state.selected_doc_ids:
                st.warning("No documents selected. Please check some boxes first.")
            else:
                with st.spinner(f"Processing {len(st.session_state.selected_doc_ids)} documents..."):
                    success_count = 0
                    error_count = 0
                    
                    for doc_id in st.session_state.selected_doc_ids:
                        # Find the document in manifest
                        doc_item = next((item for item in manifest if item["doc_id"] == doc_id), None)
                        
                        if not doc_item:
                            continue
                        
                        try:
                            # Build file path
                            file_path = UPLOAD_DIR / doc_item["stored_name"]
                            
                            # Step 1: Extract text from file
                            pages_data = extract_text(str(file_path))
                            
                            # Step 2: Create chunks
                            chunks = create_chunks(
                                pages_data=pages_data,
                                doc_id=doc_id,
                                source_file=doc_item["original_name"]
                            )
                            
                            # Step 3: Store chunks with embeddings in ChromaDB
                            store_chunks(chunks)
                            
                            success_count += 1
                            
                        except Exception as e:
                            st.error(f"Error processing {doc_item['original_name']}: {str(e)}")
                            error_count += 1
                    
                    # Show results
                    if success_count > 0:
                        st.success(f"Successfully processed {success_count} document(s)!")
                    if error_count > 0:
                        st.error(f"Failed to process {error_count} document(s)")


    def sort_key(item: dict):
        if sort_mode in ("Newest", "Oldest"):
            return item.get("uploaded_at", "")
        if sort_mode in ("Name (A→Z)", "Name (Z→A)"):
            return item.get("original_name", "").lower()
        if sort_mode in ("Size (Largest)", "Size (Smallest)"):
            return item.get("bytes", 0)
        return item.get("uploaded_at", "")

    reverse = sort_mode in ("Newest", "Name (Z→A)", "Size (Largest)")

    count_slot = st.empty()
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

            c1, c2, c3, c4 = st.columns([0.8, 5, 1, 1.2], vertical_alignment="center")

            # Checkbox
            with c1:
                was_selected = doc_id in st.session_state.selected_doc_ids
                is_checked = st.checkbox("", value=was_selected, key=f"use_{doc_id}")

                if is_checked != was_selected:
                    if is_checked:
                        st.session_state.selected_doc_ids.add(doc_id)
                    else:
                        st.session_state.selected_doc_ids.discard(doc_id)
                    # Persist selections to disk
                    save_selections(project_id, st.session_state.selected_doc_ids)

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

            # View button (pins viewer_doc_id)
            with c3:
                if st.button("View", key=f"view_{doc_id}", use_container_width=True):
                    st.session_state.viewer_open = True
                    st.session_state.viewer_doc_id = doc_id
                    st.rerun()

            # Delete
            with c4:
                delete_disabled = doc_id in st.session_state.selected_doc_ids
                if st.button("Delete", key=f"del_{doc_id}", use_container_width=True, disabled=delete_disabled):
                    file_path = UPLOAD_DIR / item["stored_name"]
                    if file_path.exists():
                        file_path.unlink()

                    manifest = [m for m in manifest if m["doc_id"] != doc_id]
                    save_manifest(MANIFEST_PATH, manifest)

                    st.session_state.selected_doc_ids.discard(doc_id)
                    st.session_state.pop(f"use_{doc_id}", None)

                    # Delete the chunks from ChromaDB
                    delete_document_chunks(doc_id)

                    # If you deleted the currently viewed file, close viewer
                    if st.session_state.viewer_doc_id == doc_id:
                        st.session_state.viewer_open = False
                        st.session_state.viewer_doc_id = None

                    # Persist selections to disk
                    save_selections(project_id, st.session_state.selected_doc_ids)
                    st.rerun()

    count_slot.caption(f"Selected documents: {len(st.session_state.selected_doc_ids)}")

    # -------------------------
    # Viewer dialog (ONE system)
    # -------------------------
    if st.session_state.viewer_open and st.session_state.viewer_doc_id:
        doc_id = st.session_state.viewer_doc_id
        viewing_item = next((m for m in manifest if m["doc_id"] == doc_id), None)

        if viewing_item is None:
            # file missing from manifest
            st.session_state.viewer_open = False
            st.session_state.viewer_doc_id = None
        else:
            @st.dialog(viewing_item["original_name"], width="large")
            def show_file_viewer():
                file_path = UPLOAD_DIR / viewing_item["stored_name"]
                if file_path.exists():
                    view_file(file_path, viewing_item["original_name"])
                else:
                    st.error("File not found on disk")

                if st.button("Close", use_container_width=True):
                    st.session_state.viewer_open = False
                    st.session_state.viewer_doc_id = None
                    st.rerun()

            show_file_viewer()

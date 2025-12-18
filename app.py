import streamlit as st
import PyPDF2
from io import BytesIO
import base64
import time

def initialize_session_state():
    # Initializing the current page
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Chat'

    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []

    if 'rag_uploader_key' not in st.session_state:
        st.session_state.rag_uploader_key = 0

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
                
    
    </style>
    """, unsafe_allow_html=True)


    # Two columns, title and then uploader
    col1, col2 = st.columns([2.5, 1.25])

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
            file_name = f.name
            file_bytes = f.getvalue()

            #TODO
            #ingest_into_rag(f.name, f.bytes)
        
        # clear uploader so nothing is stoored
        st.session_state.rag_uploader_key += 1
        st.rerun()

    # Divider
    st.markdown("""
        <hr style="margin-top: -1rem; margin-bottom: 1rem; width: 91%">
    """, unsafe_allow_html=True)


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
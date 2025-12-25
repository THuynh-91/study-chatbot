import streamlit as st
from views.chat import render_chat_page
from views.file_manager import render_file_manager_page


def initialize_session_state():
    # Initializing the current page
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Chat'

    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []

    if 'rag_uploader_key' not in st.session_state:
        st.session_state.rag_uploader_key = 0

    if "sort_mode" not in st.session_state:
        st.session_state.sort_mode = "Newest"

    if "viewer_open" not in st.session_state:
        st.session_state.viewer_open = False

    if "viewer_doc_id" not in st.session_state:
        st.session_state.viewer_doc_id = None


def render_sidebar():
    # Sidebar 
    with st.sidebar:
        st.title("Navigation")

        if st.button("New Chat", use_container_width = True):
            st.session_state.current_page = "Chat"
            # Close viewer when switching pages
            st.session_state.viewer_open = False
            st.session_state.viewer_doc_id = None

        if st.button("File Manager", use_container_width = True):
            st.session_state.current_page = "File Manager"
            # Close viewer when switching pages
            st.session_state.viewer_open = False
            st.session_state.viewer_doc_id = None


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
import streamlit as st
import PyPDF2
from io import BytesIO
import base64
import time

def main():
    # Page config
    st.set_page_config(
        page_title="Study Chatbot",
        page_icon="🎓",
        layout="wide"
    )

    # Sidebar 
    with st.sidebar:
        st.title("Navigation")

        if st.button("New Chat", use_container_width = True):
            st.session_state.current_page = "Chat"

        if st.button("File Manager", use_container_width = True):
            st.session_state.current_page = "File Manager"
    
    if st.session_state.current_page == "Chat":
        st.title("Chat")
        st.info("Chat page - WIP")

    elif st.session_state.current_page == "File Manager":
        st.title("File Manager")
        st.info("Upload Files for RAG (TBA)")


if __name__ == "__main__":
    main()
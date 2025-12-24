import streamlit as st


def render_chat_page():
    if st.session_state.current_page == "Chat":
        st.title("Chat")
        st.info("Chat page - WIP")

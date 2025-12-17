import streamlit as st
import PyPDF2
from io import BytesIO
import base64

# Page config
st.set_page_config(
    page_title="Study Chatbot",
    page_icon="🎓",
    layout="wide"
)

# Initialize session state for storing uploaded files
# TODO: Create a list to store uploaded files that persists across reruns
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []


# Title
st.title("Study Chatbot")
st.markdown("Your lectures, searchable and grounded.")

# Sidebar
with st.sidebar:
    st.header("Upload Your Materials")

    # File uploader - now accepts multiple files
    uploaded_files = st.file_uploader(
        "Upload PDFs",
        type=['pdf'],
        help="Upload your lecture notes or textbooks",
        accept_multiple_files=True  # This enables multiple file uploads
    )

    # TODO: Update session state with newly uploaded files
    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files

    # File Box - Display all uploaded files
    if uploaded_files:
        st.markdown("---")
        st.subheader("File Box")
        for file in st.session_state.uploaded_files:
            st.write(f"{file.name}")
    # TODO: Check if there are files in session state
    # TODO: Show a header "File Box" with count of files
    # TODO: Loop through each file and display:
    #       - File name with an icon
    #       - A remove button next to each file

# Main area
# TODO: Check if session state has any uploaded files
# If no files, show the welcome message
if not st.session_state.uploaded_files:  # Replace this condition
    st.info("Upload a PDF to get started!")
    st.markdown("""
    ### What is this?
    Study Chatbot helps you study by making your lecture materials searchable.
    """)

else:
    # TODO: Add a file selector so user can choose which file to view
    # HINT: Use st.selectbox() to let user pick from uploaded files

    selected_file = st.selectbox(
        "Select a file to view:",
        options = st.session_state.uploaded_files,
        format_func = lambda x: x.name
    )

    # Process the selected file
    if selected_file:
        st.success(f"Viewing: {selected_file.name}")

        # Try to extract text
        try:
            # Read the PDF
            file_bytes = selected_file.read()
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_bytes))

            num_pages = len(pdf_reader.pages)

            # Extract all text
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"

            # Show stats
            col1, col2, col3 = st.columns(3)
            col1.metric("Pages", num_pages)
            col2.metric("Characters", f"{len(text):,}")
            col3.metric("Words", f"{len(text.split()):,}")

            # Create tabs for different views
            tab1, tab2 = st.tabs(["View PDF", "Extracted Text"])

            with tab1:
                # Display PDF
                base64_pdf = base64.b64encode(file_bytes).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)

            with tab2:
                # Show text preview
                st.markdown("### Full Extracted Text")
                st.text_area("Text content", text, height=600)

            # Success message
            st.success("PDF processed successfully!")

        except Exception as e:
            st.error(f"Error reading PDF: {str(e)}")
            st.info("Try a different PDF file")
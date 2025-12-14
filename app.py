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

# Title
st.title("Study Chatbot")
st.markdown("Your lectures, searchable and grounded.")

# Sidebar
with st.sidebar:
    st.header("Upload Your Materials")
    uploaded_file = st.file_uploader(
        "Upload a PDF",
        type=['pdf'],
        help="Upload your lecture notes or textbook"
    )

# Main area
if uploaded_file is None:
    st.info("Upload a PDF to get started!")
    st.markdown("""
    ### What is this?
    Study Chatbot helps you study by making your lecture materials searchable.
    """)

else:
    st.success(f"Uploaded: {uploaded_file.name}")
    
    # Try to extract text
    try:
        # Read the PDF
        file_bytes = uploaded_file.read()
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
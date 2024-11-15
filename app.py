import streamlit as st
import tempfile
from test import main as process_cv, get_logs
import os

# Hide Streamlit footer and menu
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Initialize session state
if "processed" not in st.session_state:
    st.session_state["processed"] = False  # Whether the CV has been processed
    st.session_state["file_path"] = None  # Path to the processed file

col1, col2 = st.columns([3, 1])  # Create two columns for layout
with col1:
    st.title("CV Processing App")  # Add your title
    st.write("Upload a PDF file to process the CV")
with col2:
    st.image("logo.png", width=150)  # Add your logo

# File uploader
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Save the uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name  # Get the temporary file path

    st.write("File uploaded successfully!")

    # Check if the CV has already been processed
    if not st.session_state["processed"]:
        with st.spinner("Processing the CV, please wait..."):
            try:
                # Call the processing function and update session state
                processed_file_path = process_cv(temp_file_path)
                st.session_state["processed"] = True
                st.session_state["file_path"] = processed_file_path
                st.success("CV processed successfully. The file will be downloaded automatically.")
            except Exception as e:
                st.error(f"Error during processing: {e}")
    else:
        st.write("The CV has already been processed. You can download the file below:")

    # Display download link if the file is ready
    if st.session_state["file_path"]:
        with open(st.session_state["file_path"], "rb") as processed_file:
            st.download_button(
                label="Download Processed CV",
                data=processed_file,
                file_name="Processed_CV.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

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
if "uploaded_file" not in st.session_state:
    st.session_state["uploaded_file"] = None
if "processed_file" not in st.session_state:
    st.session_state["processed_file"] = None  # Path to the processed CV
if "logs" not in st.session_state:
    st.session_state["logs"] = ""

col1, col2 = st.columns([3, 1])  # Create two columns for layout
with col1:
    st.title("CV Processing App")  # Add your title
    st.write("Upload a PDF file to process the CV")
with col2:
    st.image("logo.png", width=150)  # Add your logo

# File uploader
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Check if a new file has been uploaded
    if uploaded_file != st.session_state["uploaded_file"]:
        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name  # Get the temporary file path

        st.session_state["uploaded_file"] = uploaded_file
        st.session_state["processed_file"] = None  # Reset processed file state

        st.write("File uploaded successfully!")

        # Process the new CV
        with st.spinner("Processing the CV, please wait..."):
            try:
                processed_file_path = process_cv(temp_file_path)
                st.session_state["processed_file"] = processed_file_path
                st.success("CV processed successfully.")
            except Exception as e:
                st.error(f"Error during processing: {e}")
                st.session_state["logs"] = get_logs()

# If a file has been processed, display the download button
if st.session_state["processed_file"]:
    with open(st.session_state["processed_file"], "rb") as processed_file:
        st.download_button(
            label="Download Processed CV",
            data=processed_file,
            file_name="Processed_CV.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

# Display logs (optional)
st.write("### Error Logs")
logs = st.session_state["logs"] if "logs" in st.session_state else get_logs()
if logs.strip():
    st.text_area("Logs", logs, height=300)
else:
    st.write("No logs to display.")

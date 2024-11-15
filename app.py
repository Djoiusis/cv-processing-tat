import streamlit as st
import tempfile
from test import main as process_cv, generate_cv
import os

# Hide Streamlit footer and menu
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Initialize session state to track processing
if "processed" not in st.session_state:
    st.session_state.processed = False
if "processed_file_path" not in st.session_state:
    st.session_state.processed_file_path = None

# Layout with columns
col1, col2 = st.columns([3, 1])
with col1:
    st.title("CV Processing App")
    st.write("Upload a PDF file to process the CV")
with col2:
    st.image("logo.png", width=150)

# File uploader
if not st.session_state.processed:
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None and not st.session_state.processed:
    # Save the uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name  # Get the temporary file path

    st.write("File uploaded successfully!")
    try:
        # Process the CV
        candidate_data = process_cv(temp_file_path)

        # Generate the CV
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as output_file:
            output_file_path = output_file.name
        generate_cv("CV-TalentAccessTechnologies-TechnicalBusinessAnalyst-DotNet.docx", candidate_data, output_file_path)

        # Save the processed file path in session state
        st.session_state.processed_file_path = output_file_path
        st.session_state.processed = True
        st.success("CV processed successfully!")

    except Exception as e:
        st.error(f"Erreur pendant le traitement : {e}")

# Download button for processed CV
if st.session_state.processed:
    if st.session_state.processed_file_path and os.path.exists(st.session_state.processed_file_path):
        with open(st.session_state.processed_file_path, "rb") as file:
            st.download_button(
                label="Download Processed CV",
                data=file,
                file_name="CV_Output_Formatted.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
    else:
        st.error("Processed file not found.")

# Reset button to allow new processing
if st.session_state.processed:
    if st.button("Upload a new CV"):
        st.session_state.processed = False
        st.session_state.processed_file_path = None

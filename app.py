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

    # Show a spinner while processing
    with st.spinner("Processing the CV, please wait..."):
        try:
            # Call the processing function
            process_cv(temp_file_path)  # This will handle downloading in `test.py`

            # Confirm success
            st.success("CV processed successfully. The file will be downloaded automatically.")
        except Exception as e:
            st.error(f"Error during processing: {e}")

# Display logs (optional)
st.write("### Error Logs")
logs = get_logs()
if logs.strip():
    st.text_area("Logs", logs, height=300)
else:
    st.write("No logs to display.")

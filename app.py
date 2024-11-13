import streamlit as st
from test import main as process_cv, get_logs  # Import get_logs function
import os

# Page layout: Title and logo
col1, col2 = st.columns([3, 1])
with col1:
    st.title("CV Processing App")
with col2:
    st.image("logo.png", width=100)

# Description text and file uploader
st.write("Upload a PDF file to process the CV")

# File uploader
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Save the uploaded file to a temporary location
    pdf_path = "uploaded_cv.pdf"
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.write("File uploaded successfully!")

    # Process the uploaded file
    try:
        process_cv(pdf_path)  # Process the uploaded PDF
        st.success("CV processed successfully!")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Display logs on the screen
st.write("### Error Logs")
logs = get_logs()
if logs.strip():  # If logs are not empty
    st.text_area("Logs", logs, height=300)
else:
    st.write("No logs to display.")

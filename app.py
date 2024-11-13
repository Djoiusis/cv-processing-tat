import streamlit as st
from test import main as process_cv, generate_cv, get_logs
import os
import json

# Initialize session state
if "candidate_data" not in st.session_state:
    st.session_state["candidate_data"] = None
if "processed_file_path" not in st.session_state:
    st.session_state["processed_file_path"] = None

# Page layout
st.title("CV Processing App")
st.write("Upload a PDF file to process the CV")

# File uploader
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
template_path = "CV-TalentAccessTechnologies-TechnicalBusinessAnalyst-DotNet.docx"
output_path = "CV_Output_Formatted.docx"

# Display real-time logs
st.write("### Logs en Temps Réel")
log_box = st.empty()  # Placeholder for logs

if uploaded_file is not None:
    pdf_path = "uploaded_cv.pdf"
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.write("File uploaded successfully!")

    try:
        # Process the PDF and structure data
        if st.session_state["candidate_data"] is None:
            st.session_state["candidate_data"] = process_cv(pdf_path)

        candidate_data = st.session_state["candidate_data"]

        # Check if valid candidate data was returned
        if candidate_data is None:
            st.error("No valid candidate data found.")
            st.stop()

        # Generate the CV
        if st.session_state["processed_file_path"] is None:
            st.session_state["processed_file_path"] = generate_cv(template_path, candidate_data, output_path)

        processed_file_path = st.session_state["processed_file_path"]

        # Display the download button if CV generation was successful
        if processed_file_path:
            st.success("CV processed successfully!")
            with open(processed_file_path, "rb") as processed_file:
                st.download_button(
                    label="Download Processed CV",
                    data=processed_file,
                    file_name="Processed_CV.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
        else:
            st.error("Failed to generate the CV. Check logs below.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

    # Display logs from `test.py`
    logs = get_logs()
    if logs.strip():
        st.text_area("Logs", logs, height=300, key="logs_realtime")  # Unique key for logs
    else:
        st.text_area("Logs", "Aucun log disponible.", height=300, key="logs_realtime_empty")  # Unique key for empty logs

# Display logs for debugging errors
st.write("### Error Logs")
logs = get_logs()
if logs.strip():
    st.text_area("Error Logs", logs, height=300, key="error_logs")
else:
    st.write("No logs to display.")

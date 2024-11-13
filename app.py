import streamlit as st
from test import main as process_cv, get_logs, get_temp_log_path, generate_cv
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

# Template and output paths
template_path = "CV-TalentAccessTechnologies-TechnicalBusinessAnalyst-DotNet.docx"  # Ensure this file exists
output_path = "Processed_CV"  # Name for the generated CV file

# Process the uploaded file
if uploaded_file is not None:
    pdf_path = "uploaded_cv.pdf"
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.write("File uploaded successfully!")

    try:
        # Step 1: Process the uploaded PDF
        candidate_data = process_cv(pdf_path)  # Replace with your AI processing pipeline
        if candidate_data is None:
            st.error("Failed to process the CV. Check logs below.")
        else:
            # Step 2: Generate the CV
            processed_file_path = generate_cv(template_path, candidate_data, output_path)
            if processed_file_path:
                st.success("CV processed successfully!")

                # Step 3: Provide a download button for the processed CV
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
        st.error(f"An error occurred during processing: {e}")

# Display logs in the app
st.write("### Error Logs")
logs = get_logs()
if logs.strip():
    st.text_area("Logs", logs, height=300)
else:
    st.write("No logs to display.")

# Allow the user to download the temporary log file
log_file_path = get_temp_log_path()
if os.path.exists(log_file_path):
    with open(log_file_path, "rb") as log_file:
        st.download_button(
            label="Download Error Logs",
            data=log_file,
            file_name="session_logs.txt",
            mime="text/plain",
        )
else:
    st.write("No log file available for download.")

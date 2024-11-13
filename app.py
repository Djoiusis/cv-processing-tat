import streamlit as st
from test import generate_cv, get_logs, structure_data_with_ai, extract_text_from_pdf  # Import necessary functions
import os

# Page layout: Title and logo
col1, col2 = st.columns([3, 1])
with col1:
    st.title("CV Processing App")
with col2:
    st.image("logo.png", width=100)  # Ensure the logo file exists in the same directory or provide the correct path

# Description text and file uploader
st.write("Upload a PDF file to process the CV")

# File uploader
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

# Template and output paths
template_path = "CV-TalentAccessTechnologies-TechnicalBusinessAnalyst-DotNet.docx"  # Ensure this file is in the root directory
output_path = "Processed_CV"

# Variable to store processed file path
processed_file_path = None

if uploaded_file is not None:
    # Save the uploaded file to a temporary location
    pdf_path = "uploaded_cv.pdf"
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.write("File uploaded successfully!")

    # Process the uploaded file
    try:
        # Step 1: Extract text from the uploaded PDF
        pdf_text = extract_text_from_pdf(pdf_path)
        if not pdf_text:
            st.error("Failed to extract text from the uploaded PDF. Please try another file.")
            st.stop()

        # Step 2: Structure the data using AI
        candidate_data = structure_data_with_ai(pdf_text)
        if not candidate_data:
            st.error("Failed to structure data using AI. Check logs below.")
            st.stop()

        # Step 3: Generate the CV using the template
        processed_file_path = generate_cv(template_path, candidate_data, output_path)
        if processed_file_path:
            st.success("CV processed successfully!")
        else:
            st.error("Failed to generate the CV. Check logs below.")
    except Exception as e:
        st.error(f"An error occurred during processing: {e}")

# Add the download button for the processed CV
if processed_file_path:
    with open(processed_file_path, "rb") as processed_file:
        st.download_button(
            label="Download Processed CV",
            data=processed_file,
            file_name="Processed_CV.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

# Display logs on the screen
st.write("### Error Logs")
logs = get_logs()
if logs.strip():  # If logs are not empty
    st.text_area("Logs", logs, height=300)
else:
    st.write("No logs to display.")

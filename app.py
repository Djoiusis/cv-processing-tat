import streamlit as st
from test import main as process_cv, generate_cv, get_logs
import os

# Page layout
st.title("CV Processing App")
st.write("Upload a PDF file to process the CV")

# File uploader
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
template_path = "CV-TalentAccessTechnologies-TechnicalBusinessAnalyst-DotNet.docx"
output_path = "CV_Output_Formatted.docx"

# Logs section
st.write("### Logs en Temps Réel")

if uploaded_file is not None:
    pdf_path = "uploaded_cv.pdf"
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.write("File uploaded successfully!")
    try:
        # Process the CV
        candidate_data = process_cv(pdf_path)

        # Debug structured data
        st.write("Structured Data from AI:")
        st.json(candidate_data)

        # Generate the CV
        processed_file_path = generate_cv(template_path, candidate_data, output_path)

        # Check if the CV was successfully generated
        if processed_file_path:
            st.write(f"Processed file path: {processed_file_path}")  # Debugging output
            st.success("CV processed successfully!")
            with open(processed_file_path, "rb") as processed_file:
                st.download_button(
                    label="Download Processed CV",
                    data=processed_file,
                    file_name=os.path.basename(processed_file_path),
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
        else:
            st.error("Failed to generate the CV. Check logs below.")
    except Exception as e:
        st.error(f"An error occurred during processing: {e}")

# Display logs
st.write("### Logs")
logs = get_logs()
if logs.strip():
    st.text_area("Logs", logs, height=300)
else:
    st.write("No logs to display.")

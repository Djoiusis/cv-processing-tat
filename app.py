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

# Display real-time logs
st.write("### Logs en Temps Réel")
log_box = st.empty()  # Placeholder for logs

if uploaded_file is not None:
    pdf_path = "uploaded_cv.pdf"
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.write("File uploaded successfully!")

    try:
        # Step 1: Process the uploaded CV
        st.write("Processing the uploaded file...")
        candidate_data = process_cv(pdf_path)

        # Step 2: Check if candidate data was returned
        if candidate_data is None:
            st.error("Failed to process the CV. Check logs below.")
            st.write("No candidate data found.")
            st.stop()

        # Display structured data
        st.write("### Structured Data from AI")
        st.json(candidate_data)

        # Step 3: Generate the CV
        st.write("Generating the formatted CV...")
        processed_file_path = generate_cv(template_path, candidate_data, output_path)

        if processed_file_path and os.path.exists(processed_file_path):
            # Display the download button if the file exists
            st.success("CV processed successfully!")
            with open(processed_file_path, "rb") as processed_file:
                st.download_button(
                    label="Download Processed CV",
                    data=processed_file,
                    file_name=os.path.basename(processed_file_path),  # Use the file name directly
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
        else:
            st.error("Failed to generate the CV. Check logs below.")

    except Exception as e:
        st.error(f"An error occurred during processing: {e}")

    # Step 4: Display logs from `test.py`
    logs = get_logs()
    if logs.strip():
        st.text_area("Logs", logs, height=300, key="logs_realtime")  # Unique key
    else:
        st.text_area("Logs", "Aucun log disponible.", height=300, key="logs_realtime_empty")  # Unique key

# Final logs display
st.write("### Error Logs")
logs = get_logs()
if logs.strip():
    st.text_area("Logs", logs, height=300, key="error_logs")
else:
    st.write("No logs to display.")

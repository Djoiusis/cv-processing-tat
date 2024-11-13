import streamlit as st
from test import main as process_cv, generate_cv, get_logs
import os

# Initialize session state to prevent double processing
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
output_path = "Processed_CV"
st.write("### Logs en Temps Réel")
log_box = st.empty()  # Placeholder for logs

if uploaded_file is not None:
    pdf_path = "uploaded_cv.pdf"
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.write("File uploaded successfully!")

    try:
        # Process the PDF and structure data only if not already done
        if st.session_state["candidate_data"] is None:
            st.session_state["candidate_data"] = process_cv(pdf_path)

        candidate_data = st.session_state["candidate_data"]

        # Check if valid candidate data was returned
        if candidate_data is None:
            st.error("Failed to process the CV. Check logs below.")
            st.write("No candidate data found.")
            st.stop()

        # Display structured data
        st.write("Structured Data from AI:")
        st.json(candidate_data)

        # Generate the CV only if not already done
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
                    file_name=os.path.basename(processed_file_path),  # Use the file name directly
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
        else:
            st.error("Failed to generate the CV. Check logs below.")

        # Display logs from `test.py`
        logs = get_logs()
        if logs.strip():
            st.text_area("Logs", logs, height=300, key="logs_realtime")  # Unique key
        else:
            st.text_area("Logs", "Aucun log disponible.", height=300, key="logs_realtime_empty")  # Unique key

    except Exception as e:
        st.error(f"Erreur pendant le traitement : {e}")

# Display error logs at the end
st.write("### Error Logs")
logs = get_logs()
if logs.strip():
    st.text_area("Error Logs", logs, height=300, key="error_logs")
else:
    st.write("No logs to display.")

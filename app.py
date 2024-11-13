import streamlit as st
from test import main as process_cv, generate_cv, get_logs
import os

# Page layout
st.title("CV Processing App")
st.write("Upload a PDF file to process the CV")

# File uploader
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
template_path = "CV-TalentAccessTechnologies-TechnicalBusinessAnalyst-DotNet.docx"
output_path = "Processed_CV"
st.write("### Logs en Temps Réel")
log_box = st.empty()  # Place un conteneur pour les logs

if uploaded_file is not None:
    pdf_path = "uploaded_cv.pdf"

    st.write("File uploaded successfully!")
    try:
  
        candidate_data = process_cv(pdf_path)
        # Display logs from `test.py`
        logs = get_logs()
        print("Current logs:", logs)
        if logs.strip():
            st.text_area("Logs", logs, height=300, key="logs_realtime")  # Unique key
        else:
            st.text_area("Logs", "Aucun log disponible.", height=300, key="logs_realtime_empty")  # Unique key

        st.success("Traitement terminé avec succès.")
                
    except Exception as e:
        st.error(f"Erreur pendant le traitement : {e}")
if candidate_data is None:
    st.error("Failed to process the CV. Check logs below.")
    st.write("No candidate data found.")
    st.stop()
    # Display structured data
    st.write("Structured Data from AI:")
    st.json(candidate_data)

    # Generate the CV
    processed_file_path = generate_cv(template_path, candidate_data, output_path)
    if processed_file_path:
        if os.path.exists(processed_file_path):
            st.success("CV processed successfully!")
            # Add the download button for the processed CV
            with open(processed_file_path, "rb") as processed_file:
                st.download_button(
                label="Download Processed CV",
                data=processed_file,
                file_name=os.path.basename(processed_file_path),  # Correct file name
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )    
        else:
            st.error(f"File generated but not found: {processed_file_path}")
    else:
        st.error("Failed to generate the CV. Please check the logs.")


# Display logs
st.write("### Error Logs")
logs = get_logs()
if logs.strip():
    st.text_area("Logs", logs, height=300)
else:
    st.write("No logs to display.")

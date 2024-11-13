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
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.write("File uploaded successfully!")
    # Create a unique key for the text_area
    log_key = "log_area"
    log_container = st.empty()
    try:
  
        candidate_data = process_cv(pdf_path)
        # Counter for unique keys
        iteration = 0

        # Boucle pour mettre à jour les logs
        while True:
            logs = get_logs()

            # Mettre à jour les logs avec une clé unique
            log_container.text_area(
                "Logs",
                logs if logs.strip() else "Aucun log pour le moment.",
                height=300,
                key=f"log_area_{iteration}"  # Générer une clé unique
            )

            iteration += 1  # Incrémenter le compteur pour la clé

            # Sortir de la boucle si le traitement est terminé
            if "Données structurées avec succès." in logs or "Erreur inattendue" in logs:
                break

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
        st.error(f"An error occurred during processing: {e}")

# Display logs
st.write("### Error Logs")
logs = get_logs()
if logs.strip():
    st.text_area("Logs", logs, height=300)
else:
    st.write("No logs to display.")

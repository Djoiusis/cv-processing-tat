import streamlit as st
import tempfile
from test import main as process_cv, generate_cv, get_logs
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
template_path = "CV-TalentAccessTechnologies-TechnicalBusinessAnalyst-DotNet.docx"
output_path = "/tmp/CV_Output_Formatted.docx"
# st.write("### Logs")
# log_box = st.empty()  # Place un conteneur pour les logs

if uploaded_file is not None:
    # Save the uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name  # Get the temporary file path   

    st.write("File uploaded successfully!")
    try:

         with st.spinner("Processing the CV..."):
             candidate_data = process_cv(temp_file_path)
             st.success("The CV has been processed to TAT format.")
     
        # logs = get_logs()
        # print("Current logs:", logs)
        # if logs.strip():
        #    st.text_area("Logs", logs, height=300, key="logs_realtime")  # Unique key
        # else:
        #    st.text_area("Logs", "Aucun log disponible.", height=300, key="logs_realtime_empty")  # Unique key
       
        

    
                
    except Exception as e:
        st.error(f"Erreur pendant le traitement : {e}")

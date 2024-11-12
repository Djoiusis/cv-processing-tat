import streamlit as st
from test import main as process_cv  # Import the updated main function

# Create two columns for the title and logo
col1, col2 = st.columns([3, 1])  # Adjust the width ratio as needed

with col1:
    st.title("CV Processing App")

with col2:
    st.image("logo.png", width=100)  # Set the width for the logo
    
st.write("Upload a PDF file to process the CV")


# File uploader
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Save the uploaded file to a temporary location
    pdf_path = "uploaded_cv.pdf"
    output_path = "CV_Output_Formatted.docx"
    
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.write("File uploaded successfully!")

    # Process the uploaded file
    try:
        process_cv(pdf_path)  # Process the uploaded PDF
        st.success("CV processed successfully!")

        # Add download button for the generated CV
        with open(output_path, "rb") as f:
            st.download_button(
                label="Download Processed CV",
                data=f,
                file_name="Processed_CV.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

    except Exception as e:
        st.error(f"An error occurred: {e}")

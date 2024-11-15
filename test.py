import pdfplumber
import json
import openai
from openai.error import RateLimitError
import time
import streamlit as st
import datetime
import re
import os
import glob
from docxtpl import DocxTemplate
import logging
import tempfile
from io import StringIO



# Créez un buffer pour les logs
log_buffer = StringIO()
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
    
# Configurez les logs pour écrire dans le buffer
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(log_buffer),  # Écrire dans le buffer
    ],
)


def get_logs():
    log_buffer.seek(0)  # Move to the beginning of the buffer
    return log_buffer.read() or "No logs found in buffer."

# Set your OpenAI API key
openai.api_key = st.secrets["general"]["OPENAI_API_KEY"]


def cleanup_output_files(pattern="*.docx", exclude_files=None):
    """
    Delete all output files matching the specified pattern,
    excluding the files listed in exclude_files.
    """
    try:
        exclude_files = exclude_files or []  # Default to an empty list if None

        # Find all files matching the pattern
        files_to_delete = glob.glob(pattern)

        # Filter out excluded files
        files_to_delete = [file for file in files_to_delete if file not in exclude_files]

        # Delete each file
        for file_path in files_to_delete:
            os.remove(file_path)
            logging.info(f"Deleted file: {file_path}")

        logging.info("Cleanup completed successfully.")
    except Exception as e:
        logging.error(f"Error during cleanup: {e}")

    
def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = "".join(page.extract_text() for page in pdf.pages)
        logging.info(f"Extracted text length: {len(text)} characters")
        return text
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {e}", exc_info=True)
        return None


def format_date(date_str):
    """Convert French or English date strings like 'Septembre 2021' to 'MM.YYYY' format."""
    # Mapping French month names to English
    french_to_english_months = {
        "Janvier": "January", "Février": "February", "Mars": "March", "Avril": "April",
        "Mai": "May", "Juin": "June", "Juillet": "July", "Août": "August",
        "Septembre": "September", "Octobre": "October", "Novembre": "November", "Décembre": "December"
    }
    
    # Replace French month with English equivalent if present
    for fr_month, en_month in french_to_english_months.items():
        if fr_month in date_str:
            date_str = date_str.replace(fr_month, en_month)
            break  # Exit loop once replacement is made

    try:
        # Now attempt to parse the date with English month names
        date_obj = datetime.datetime.strptime(date_str, "%B %Y")
        return date_obj.strftime("%m.%Y")
    except ValueError:
        logging.warning(f"Date format not recognized for '{date_str}', leaving as is.")
        return date_str  # Return original if unable to format
        
def structure_data_with_ai(text):
    """Uses GPT-3.5 Turbo to structure the extracted CV text into JSON format with retry and error handling."""
    # Define the messages with instructions for the AI model
    messages = [
        {
            "role": "system",
            "content": "You are an assistant that organizes CV text into structured JSON. Respond with only JSON format. Output all data in French."
        },
        {
            "role": "user",
            "content": f"Organize the following CV text into a structured JSON format containing:\n"
                       f"- name (full name of the candidate),\n"
                       f"- profile (a professional summary of the candidate's experience and expertise, formatted with line breaks for readability),\n"
                       f"- title (professional title or current job title),\n"
                       f"- education (list of educational qualifications with fields:\n"
                       f"    * 'end_date' (graduation year or the year the degree was obtained, look explicitly for numbers like '2018', '2021', etc.),\n"
                       f"    * 'degree' (e.g., Master, Bachelor, extract even if incomplete),\n"
                       f"    * 'field' (e.g., Computer Science, extract explicitly),\n"
                       f"    * 'institution' (e.g., University of Lyon, extract explicitly),\n"
                       f"    * 'format' (optional, e.g., alternance, extract explicitly))\n"
                       f"Ensure the output is clear and does not add unnecessary descriptive text. If a value is missing, simply omit it."
                       f"- age (calculate age if date of birth is available, otherwise leave blank),\n"
                       f"- experience (list of roles with fields: start_date, end_date, company, location, position, clients (optional), and one or both of the following:\n"
                       f"    * 'projects' (if projects are explicitly mentioned, include:\n"
                       f"        - name (project name),\n"
                       f"        - description (brief project description),\n"
                       f"        - missions (list of responsibilities for the project))\n"
                       f"    * 'tasks' (if no projects are mentioned, include a direct list of tasks or responsibilities tied to the role))\n"
                       f"- The 'technologies' field should be a list of programming languages, software, or tools used in each role.\n\n"
                       f"- languages (a list of languages with each entry containing:\n"
                       f"    * 'name' (the language name, e.g., French, English), and\n"
                       f"    * 'proficiency' (the level of proficiency, e.g., Native, Fluent, Conversational))\n"         
                       f"- skills, organized into:\n"
                       f"    * 'technical_skills' (required for all candidates, includes programming languages, frameworks, databases, cloud/DevOps tools, etc.),\n"
                       f"    * 'project_skills' (consolidates soft skills, project management tools, and collaboration tools if relevant for the role)\n"                       f"Classify the skills intelligently based on the role and expertise.\n\n"
                       f"Classify the skills intelligently based on the role and expertise.\n\n"
                       f"CV Text:\n{text}"
        }
    ]

     # Exponential backoff retry mechanism for handling RateLimitError
    wait_time = 30  # Start with a 30-second wait time
    for attempt in range(5):  # Retry up to 5 times
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Use gpt-3.5-turbo or gpt-4-turbo if accessible
                messages=messages,
                max_tokens=1500
            )
            raw_output = response.choices[0].message['content'].strip()
            logging.info("Data successfully structured by AI.")
            # Clean the raw output to ensure it starts and ends with curly braces
            cleaned_output = re.sub(r'^[^{]*|[^}]*$', '', raw_output)

            # Attempt to parse the cleaned JSON
            structured_data = json.loads(cleaned_output)
            
    # Apply date formatting to experience dates
            for exp in structured_data.get("experience", []):
                original_start = exp.get("start_date", "")
                original_end = exp.get("end_date", "")
                exp["start_date"] = format_date(original_start)
                exp["end_date"] = format_date(original_end)
                logging.info(f"Formatted '{original_start}' to '{exp['start_date']}', '{original_end}' to '{exp['end_date']}'")
            
            # Save the structured data to an output JSON file
            with open('output_data.json', 'w') as json_file:
                json.dump(structured_data, json_file, indent=4, ensure_ascii=False)
            logging.info("Structured data saved to output_data.json.")
            logging.info("Données structurées avec succès.")
            return structured_data

        except json.JSONDecodeError as e:
            logging.error(f"JSON decoding error: {e}")
            continue  # Skip to the next attempt

        except openai.error.RateLimitError:
            logging.warning(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            wait_time *= 2  # Exponential backoff

        except Exception as e:
            logging.error(f"An unexpected error occurred while structuring data with AI: {e}")
            break
    return None



def generate_cv(template_path, data, output_path):
    """Generates the CV using the specified template and structured data."""
    try:
        logging.info(f"Current working directory: {os.getcwd()}")
        logging.info(f"Files in directory: {os.listdir(os.getcwd())}")
        logging.info(f"Looking for template at: {template_path}")
        # Cleanup previous output files
        #cleanup_output_files("*.docx", exclude_files=[template_path])

        if not os.path.exists(template_path):
            logging.error(f"Template file not found at {template_path}")
            return None

        if data is None or not isinstance(data, dict):
            logging.error("Invalid or missing data for CV generation.")
            return None

        # Generate a unique temporary file each time
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
            temp_file_path = temp_file.name
            logging.info(f"Temporary file created at: {temp_file_path}")

        # Generate the CV and save it to the temporary file
        doc = DocxTemplate(template_path)
        doc.render(data)
        logging.info("Template rendered successfully.")
        doc.save(temp_file_path)
        logging.info(f"CV generated successfully at {temp_file_path}")

        # Provide the file for automatic download directly from `test.py`
        with open(temp_file_path, "rb") as file:
            st.download_button(
                label="Download Processed CV",
                data=file,
                file_name="Processed_CV.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )

        return temp_file_path
    except Exception as e:
        logging.error(f"Error generating CV: {e}")
        return None



def main(pdf_path):
    # File paths
    logging.info(f"Début du traitement du fichier : {pdf_path}")
    template_path = 'CV-TalentAccessTechnologies-TechnicalBusinessAnalyst-DotNet.docx'
    output_path = 'CV_Output_Formatted.docx'
    # Step 1: Extract text from PDF
    pdf_text = extract_text_from_pdf(pdf_path)
    if pdf_text is None:
        logging.error("Failed to extract text from PDF. Exiting.")
        return
    
    # Step 2: Structure data with AI
    candidate_data = structure_data_with_ai(pdf_text)
    if candidate_data is None:
        logging.error("Failed to structure data with AI. Exiting.")
        return
    
    # Step 3: Populate the template with data if extraction was successful
    if not candidate_data or not isinstance(candidate_data, dict):
        logging.error("Candidate data is invalid or missing. Aborting CV generation.")
        st.error("Candidate data is invalid or missing. Please check the logs.")
        st.stop()

     # Step 3: Generate the CV
    processed_file_path = generate_cv(template_path, candidate_data, output_path)
    if not processed_file_path:
        logging.error("Failed to generate the CV.")
        return None
    logging.info(f"CV successfully generated at: {processed_file_path}")

    return processed_file_path


if __name__ == "__main__":
    main()

import pdfplumber
import json
import openai
import time
import datetime
import re
import os
from docxtpl import DocxTemplate
import logging

# Set up logging
logging.basicConfig(filename='process_log.txt', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Set your OpenAI API key
openai.api_key = "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"


def extract_text_from_pdf(pdf_path):
    """Extracts all text from a PDF file."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = "".join(page.extract_text() for page in pdf.pages)
        logging.info("PDF text extracted successfully.")
        return text
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {e}")
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
            "content": "You are an assistant that organizes CV text into structured JSON. Respond with only JSON format."
        },
        {
            "role": "user",
            "content": f"Organize the following CV text into a structured JSON format containing:\n"
                       f"- name (full name of the candidate),\n"
                       f"- profile (a professional summary of the candidate's experience and expertise, formatted with line breaks for readability),\n"
                       f"- title (professional title or current job title),\n"
                       f"- education (list of educational qualifications with fields:\n"
                       f"    * 'end_date' (graduation year or the year the degree was obtained),\n"
                       f"    * 'degree' (e.g., Master, Bachelor),\n"
                       f"    * 'field' (e.g., Computer Science),\n"
                       f"    * 'institution' (e.g., University of Lyon),\n"
                       f"    * 'format' (optional, e.g., alternance))\n"
                       f"- age (calculate age if date of birth is available, otherwise leave blank),\n"
                       f"- experience (list of roles with fields: start_date, end_date, company, location, position, clients (optional), projects)\n"
                       f"- Each project should contain: name, description, and missions (list of responsibilities)\n\n"
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
    """Populates the CV template with structured data."""
    # Check if the template file exists
    if not os.path.exists(template_path):
        logging.error(f"Template file not found at {template_path}")
        return

    try:
        # Generate a unique file name for the output
        unique_output_path = f"{output_path}_{uuid.uuid4().hex[:8]}.docx"

        # Load the template and render with structured data
        doc = DocxTemplate(template_path)
        doc.render(data)
        doc.save(unique_output_path)
        logging.info(f"CV generated successfully at {unique_output_path}")
        return unique_output_path
    except Exception as e:
        logging.error(f"Error generating CV: {e}")
        return None

def main(pdf_path):
    # File paths
    template_path = 'C:/Users/karim/Downloads/CV/CV-TalentAccessTechnologies-TechnicalBusinessAnalyst-DotNet.docx'  # Path to the Word template
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
    generate_cv(template_path, candidate_data, output_path)

if __name__ == "__main__":
    main()

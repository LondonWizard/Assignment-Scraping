import docx
from instructor import from_openai, Mode
from pydantic import BaseModel, Field
from typing import List
from openai import OpenAI
from config import parse_assignments_from_text


def extract_text_from_docx(docx_file):
    """
    Extracts text from a DOCX file.

    Args:
    - docx_file (str): The path to the DOCX file.

    Returns:
    - str: The extracted text from the DOCX file.
    """
    doc = docx.Document(docx_file)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def extract_assignments_from_docx(docx_file):
    """
    Extracts assignments from a DOCX file using GPT-4 and the Instructor client.

    Args:
    - docx_file (str): The path to the DOCX file.

    Returns:
    - List[Assignment]: A list of extracted assignments in structured format.
    """
    try:
        # Extract the text from the DOCX file
        docx_text = extract_text_from_docx(docx_file)
        return parse_assignments_from_text(docx_text)
        # Define the prompt to ask GPT to extract assignments
        

    except Exception as e:
        print(f"Error while extracting assignments from DOCX: {e}")
        return None
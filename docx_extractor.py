import docx
from instructor import from_openai, Mode
from pydantic import BaseModel, Field
from typing import List
from openai import OpenAI
from config import OPENAI_API_KEY

# Define the Assignment model (for structured response)
class Assignment(BaseModel):
    title: str = Field(description="The title of the assignment")
    due_date: str = Field(description="The due date of the assignment")
    description: str = Field(description="A brief description of the assignment")

class MultiAssignment(BaseModel):
    tasks: List[Assignment] = Field(description="List of assignments extracted from the document")

# Initialize the OpenAPI Client with Instructor
client = OpenAI(
  api_key=OPENAI_API_KEY
)
client = from_openai(client)

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
        
        # Define the prompt to ask GPT to extract assignments
        prompt = (
            "You are tasked with extracting assignments from the following DOCX content. "
            "Please provide a list of assignments with titles, due dates, and brief descriptions. Format the due dates in python datetime library format.\n\n"
            f"Text:\n{docx_text}"
        )
        
        # Call GPT model with structured response model MultiAssignment using the Instructor client
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_model=MultiAssignment,  # Expect structured response
            max_retries=3  # Using structured mode for well-defined output
        )

        # Return the list of assignments
        return resp.tasks  # This returns a list of Assignment objects

    except Exception as e:
        print(f"Error while extracting assignments from DOCX: {e}")
        return None
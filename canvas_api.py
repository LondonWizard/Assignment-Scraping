import requests
from config import CANVAS_API_KEY, CANVAS_BASE_URL
from pydantic import BaseModel, Field
from openai import OpenAI
from instructor import from_openai, Mode
from typing import List
from google.oauth2.credentials import Credentials
from config import OPENAI_API_KEY

headers = {
    'Authorization': f'Bearer {CANVAS_API_KEY}'
}

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


def get_assignments(course_id):
    url = url = f'{CANVAS_BASE_URL}/courses/{course_id}/assignments?access_token={CANVAS_API_KEY}'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_pdf_content(course_id, file_id):
    url = f'{CANVAS_BASE_URL}/courses/{course_id}/files/{file_id}?access_token={CANVAS_API_KEY}'
    response = requests.get(url)
    response.raise_for_status()
    file_url = response.json()['url']
    
    # Download the PDF
    pdf_response = requests.get(file_url)
    with open('file.pdf', 'wb') as f:
        f.write(pdf_response.content)

    return 'file.pdf'


def get_docx_content(course_id, file_id):
    """
    Downloads DOCX content from a course file in Canvas.

    Args:
    - course_id (str): The ID of the course.
    - file_id (str): The ID of the file to download.

    Returns:
    - str: The local file path where the DOCX file is saved.
    """
    url = f'{CANVAS_BASE_URL}/courses/{course_id}/files/{file_id}?access_token={CANVAS_API_KEY}'
    response = requests.get(url)
    response.raise_for_status()
    file_url = response.json()['url']
    
    # Download the DOCX file
    docx_response = requests.get(file_url)
    local_filename = 'file.docx'
    with open(local_filename, 'wb') as f:
        f.write(docx_response.content)

    return local_filename



def extract_assignments_content(course_id):
    try:
        assignments = get_assignments(course_id)
        # Define the prompt to ask GPT to extract assignments
        prompt = (
            "You are tasked with extracting assignments from the following canvas api assignments array. "
            "Please provide a list of assignments with titles, due dates, and brief descriptions. Format the times in python datetime library format.\n\n"
            f"Text:\n{assignments}"
        )
        #print(prompt)
        
        # Call GPT model with structured response model MultiAssignment using the Instructor client
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_model=MultiAssignment,  # Expect structured response
            max_retries=8,  # Retry up to 8 times
        )
        print(resp.tasks)
        # Return the list of assignments
        return resp.tasks  # This returns a list of Assignment objects

    except Exception as e:
        print(f"Error while scraping Canvas Assignments: {e}")
        return None

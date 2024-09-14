from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from instructor import from_openai, Mode
from pydantic import BaseModel, Field
from typing import List
from config import OPENAI_API_KEY
from openai import OpenAI

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

def get_google_doc_content(doc_id, creds):
    """
    Fetches the content of a Google Doc.
    
    Args:
    - doc_id (str): The ID of the Google Doc.
    - creds (Credentials): The Google OAuth credentials.
    
    Returns:
    - str: The text content of the Google Doc.
    """
    service = build('docs', 'v1', credentials=creds)
    document = service.documents().get(documentId=doc_id).execute()
    doc_content = document.get('body').get('content')

    # Extract text from the Google Doc
    text = ''.join([item.get('paragraph').get('elements')[0].get('textRun').get('content') 
                    for item in doc_content if 'paragraph' in item])
    
    return text

def scrape_google_doc(doc_id, creds):
    """
    Scrapes Google Doc content and extracts assignments using GPT-4 with the Instructor library.

    Args:
    - doc_id (str): The ID of the Google Doc.
    - creds (Credentials): The Google OAuth credentials.
    
    Returns:
    - List[Assignment]: A list of extracted assignments in structured format.
    """
    try:
        # Fetch the Google Doc content
        text = get_google_doc_content(doc_id, creds)
        
        # Define the prompt to ask GPT to extract assignments
        prompt = (
            "You are tasked with extracting assignments from the following Google Docs content. "
            "Please provide a list of assignments with titles, due dates, and brief descriptions.\n\n"
            f"Text:\n{text}"
        )
        
        # Call GPT model with structured response model MultiAssignment using the Instructor client
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_model=MultiAssignment,  # Expect structured response
            mode=Mode.STRUCTURED  # Using structured mode
        )

        # Return the list of assignments
        return resp.tasks  # This returns a list of Assignment objects

    except Exception as e:
        print(f"Error while scraping Google Docs: {e}")
        return None
import os
from pydantic import BaseModel, Field
from typing import List
from openai import OpenAI
from instructor import from_openai, Mode

CANVAS_API_KEY = os.environ.get("CANVAS_API_KEY")
CANVAS_BASE_URL = 'https://hub.hw.com/api/v1'
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(
  api_key=OPENAI_API_KEY
)
client = from_openai(client)

class Assignment(BaseModel):
    title: str = Field(description="The title of the assignment")
    due_date: str = Field(description="The due date of the assignment")
    description: str = Field(description="A brief description of the assignment")

class MultiAssignment(BaseModel):
    tasks: List[Assignment] = Field(description="List of assignments extracted from the document")


def parse_assignments_from_text(text):
    prompt = (
            "You are tasked with extracting assignments from the following content. "
            "Please provide a list of assignments with titles, due dates, and brief descriptions. Format the due dates in python datetime library format.\n\n"
            f"Text:\n{text}"
        )
        
        # Call GPT model with structured response model MultiAssignment using the Instructor client
    resp = client.chat.completions.create(
        model="o1-preview",
        messages=[
            {"role": "user", "content": prompt}
        ],
        response_model=MultiAssignment,  # Expect structured response
        max_retries=8  # Using structured mode for well-defined output
    )

        # Return the list of assignments
    return resp.tasks  # This returns a list of Assignment objects
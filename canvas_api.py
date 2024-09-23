import requests
from config import CANVAS_API_KEY, CANVAS_BASE_URL, parse_assignments_from_text

headers = {
    'Authorization': f'Bearer {CANVAS_API_KEY}'
}


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
        return parse_assignments_from_text(assignments)

    except Exception as e:
        print(f"Error while scraping Canvas Assignments: {e}")
        return None

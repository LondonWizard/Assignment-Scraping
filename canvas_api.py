# canvas_api.py

import requests
from config import CANVAS_BASE_URL, parse_assignments_from_text, Assignment, MultiAssignment

def get_assignments(course_id, access_token):
    assignments = []
    url = f'{CANVAS_BASE_URL}/api/v1/courses/{course_id}/assignments'
    params = {'per_page': 100}  # Fetch up to 100 assignments per page
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    while url:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        page_assignments = response.json()
        assignments.extend(page_assignments)
        print(f"Retrieved {len(page_assignments)} assignments from {url}")
        
        # Check for 'next' link in the 'Link' header
        if 'Link' in response.headers:
            links = requests.utils.parse_header_links(response.headers['Link'].rstrip('>').replace('>,<', ',<'))
            next_url = None
            for link in links:
                if link.get('rel') == 'next':
                    next_url = link['url']
                    break
            url = next_url
            params = None  # Parameters are included in the next_url
        else:
            url = None  # No more pages to fetch

    print(f"Total assignments retrieved: {len(assignments)}")
    return assignments

def list_files(course_id, access_token):
    files = []
    url = f'{CANVAS_BASE_URL}/api/v1/courses/{course_id}/files'
    params = {'per_page': 100}
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    while url:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        page_files = response.json()
        files.extend(page_files)
        print(f"Retrieved {len(page_files)} files from {url}")

        # Check for 'next' link in the 'Link' header
        if 'Link' in response.headers:
            links = requests.utils.parse_header_links(
                response.headers['Link'].rstrip('>').replace('>,<', ',<'))
            next_url = None
            for link in links:
                if link.get('rel') == 'next':
                    next_url = link['url']
                    break
            url = next_url
            params = None  # Parameters are included in the next_url
        else:
            url = None  # No more pages to fetch

    print(f"Total files retrieved: {len(files)}")
    return files

def get_pdf_content(course_id, file_id, access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    url = f'{CANVAS_BASE_URL}/api/v1/courses/{course_id}/files/{file_id}'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    file_url = response.json()['url']
    
    # Download the PDF
    pdf_response = requests.get(file_url, headers=headers)
    with open('file.pdf', 'wb') as f:
        f.write(pdf_response.content)

    return 'file.pdf'

def get_docx_content(course_id, file_id, access_token):
    """
    Downloads DOCX content from a course file in Canvas.

    Args:
    - course_id (str): The ID of the course.
    - file_id (str): The ID of the file to download.
    - access_token (str): The user's access token.

    Returns:
    - str: The local file path where the DOCX file is saved.
    """
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    url = f'{CANVAS_BASE_URL}/api/v1/courses/{course_id}/files/{file_id}'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    file_url = response.json()['url']
    
    # Download the DOCX file
    docx_response = requests.get(file_url, headers=headers)
    local_filename = 'file.docx'
    with open(local_filename, 'wb') as f:
        f.write(docx_response.content)

    return local_filename

def extract_assignments_content(course_id, access_token):
    try:
        assignments_data = get_assignments(course_id, access_token)
        assignment_objects = []
        for assignment in assignments_data:
            name = assignment.get('name')
            description = assignment.get('description') or ''
            due_at = assignment.get('due_at')
            if due_at:
                # Create an Assignment object
                assignment_obj = Assignment(
                    title=name,
                    description=description,
                    due_date=due_at
                )
                assignment_objects.append(assignment_obj)
            else:
                print(f"Assignment '{name}' does not have a due date and will be skipped.")
        # Return a MultiAssignment object
        multi_assignment = MultiAssignment(tasks=assignment_objects)
        return multi_assignment
    except Exception as e:
        print(f"Error while extracting Canvas Assignments: {e}")
        return MultiAssignment(tasks=[])
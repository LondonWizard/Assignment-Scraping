import canvas_api
import pdf_extractor
import gpt_api
import google_docs_extractor
from google.oauth2.credentials import Credentials
import docx_extractor

def main():
    # Get Assignments from Canvas API
    SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
    history_course_id = '3511481'
    assignments = canvas_api.extract_assignments_content(history_course_id)
    print("Canvas Assignments:")
    print(assignments)
    
    french_course_id = '3511422'
    french_assignment_file_id = '253166518'

    french_doc = canvas_api.get_docx_content(french_course_id, french_assignment_file_id)
    french_assignments = docx_extractor.extract_assignments_from_docx(french_doc)
    print("French Assignments: ")
    print(french_assignments)

    # Extract PDF content and use GPT to summarize (structured output)
    """
    file_id = ''
    pdf_path = canvas_api.get_pdf_content('3511422', file_id)
    pdf_text = pdf_extractor.extract_text_from_pdf(pdf_path)
    pdf_assignments = gpt_api.gpt_extract_assignments(pdf_text)  # Now returns structured assignment data
    if pdf_assignments:
        for assignment in pdf_assignments:
            print(f"Assignment: {assignment.title}, Due: {assignment.due_date}, Description: {assignment.description}")
    """
    # Scrape Google Docs and extract assignments (structured output)
    """
    doc_id = 'your_google_doc_id'
    creds = Credentials.from_authorized_user_file('credentials.json', SCOPES)
    google_doc_assignments = google_docs_extractor.scrape_google_doc(doc_id, creds)  # Structured response
    if google_doc_assignments:
        for assignment in google_doc_assignments:
            print(f"Assignment: {assignment.title}, Due: {assignment.due_date}, Description: {assignment.description}")
"""
if __name__ == "__main__":
    main()
    
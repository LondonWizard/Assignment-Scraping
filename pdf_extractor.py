import PyPDF2
from config import parse_assignments_from_text

def extract_assignments_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return parse_assignments_from_text(text)


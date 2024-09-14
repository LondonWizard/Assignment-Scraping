from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import openai
from config import OPENAI_API_KEY

SCOPES = ['https://www.googleapis.com/auth/documents.readonly']

def get_google_doc_content(doc_id, creds):
    service = build('docs', 'v1', credentials=creds)
    document = service.documents().get(documentId=doc_id).execute()
    return document.get('body').get('content')

def scrape_google_doc(doc_id, creds):
    doc_content = get_google_doc_content(doc_id, creds)
    text = ''.join([item.get('paragraph').get('elements')[0].get('textRun').get('content') for item in doc_content if 'paragraph' in item])
    
    return gpt_extract_assignments(text)

def gpt_extract_assignments(text):
    openai.api_key = OPENAI_API_KEY
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an instructor extracting assignments from Google Docs."},
            {"role": "user", "content": f"Extract assignments from the following Google Docs content:\n{text}"}
        ]
    )
    return response['choices'][0]['message']['content']
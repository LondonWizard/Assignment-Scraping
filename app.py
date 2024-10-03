# app.py

import os
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from datetime import datetime, timedelta
import canvas_api
import pdf_extractor
import docx_extractor
import json
import traceback
import requests
import secrets
from config import CANVAS_API_KEY

app = Flask(__name__)

# Set the secret key for session management
app.secret_key = os.environ.get('FLASK_SECRET_KEY')

# Canvas OAuth2 configuration
CANVAS_BASE_URL = 'https://canvas.instructure.com'  # Replace if using a different Canvas instance

REDIRECT_URI = 'https://yourdomain.com/oauth2callback'  # Replace with your actual domain

# Path to the JSON file where classes data will be stored
CLASSES_FILE = 'classes_data.json'

# Function to load classes from the JSON file
def load_classes():
    if os.path.exists(CLASSES_FILE):
        with open(CLASSES_FILE, 'r') as f:
            classes = json.load(f)
            print("Loaded classes from file:", classes)
            return classes
    else:
        print("Classes file not found. Starting with empty classes list.")
        return []

# Function to save classes to the JSON file
def save_classes(classes):
    with open(CLASSES_FILE, 'w') as f:
        json.dump(classes, f)
        print("Classes saved to file.")

# Route to serve the main HTML page
@app.route('/')
def index():
    return render_template('index.html')

# Route to start the OAuth2 login flow
@app.route('/login')
def login():
    state = secrets.token_urlsafe(16)
    session['oauth_state'] = state
    canvas_authorize_url = f"{CANVAS_BASE_URL}/login/oauth2/auth"
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'state': state,
        # Specify the scopes your app needs; adjust as necessary
        'scope': 'url:GET|/api/v1/courses url:GET|/api/v1/courses/:course_id/assignments url:GET|/api/v1/courses/:course_id/files'
    }
    url = requests.Request('GET', canvas_authorize_url, params=params).prepare().url
    return redirect(url)

# Route to handle the OAuth2 callback
@app.route('/oauth2callback')
def oauth2callback():
    error = request.args.get('error')
    if error:
        return f"Error: {error}"

    state = request.args.get('state')
    if state != session.get('oauth_state'):
        return "Error: Invalid state parameter"

    code = request.args.get('code')
    if not code:
        return "Error: No code provided."

    # Exchange code for access token
    token_url = f"{CANVAS_BASE_URL}/login/oauth2/token"
    data = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'code': code
    }
    response = requests.post(token_url, data=data)
    if response.status_code != 200:
        return f"Error fetching token: {response.text}"

    token_info = response.json()
    access_token = token_info['access_token']
    refresh_token = token_info.get('refresh_token')

    # Store tokens in the session
    session['access_token'] = access_token
    session['refresh_token'] = refresh_token

    # Redirect to the main page or dashboard
    return redirect(url_for('index'))

# Route to logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# API endpoint to add or update classes
@app.route('/classes', methods=['GET', 'POST'])
def manage_classes():
    if request.method == 'POST':
        data = request.json
        print("Received data to save classes:", data)
        classes = data.get('classes', [])
        save_classes(classes)
        return jsonify({'message': 'Classes saved successfully.'}), 200
    else:
        classes = load_classes()
        return jsonify({'classes': classes}), 200

# API endpoint to fetch assignments
@app.route('/fetch-assignments', methods=['POST'])
def fetch_assignments():
    # Check if user is authenticated
    #if 'access_token' not in session:
        #return redirect(url_for('login'))

    access_token = CANVAS_API_KEY #session['access_token']
    data = request.json
    print("Received data:", data)

    # Load classes from the file if not provided in the request
    if not data or 'classes' not in data:
        classes = load_classes()
    else:
        classes = data.get('classes', [])
    print("Classes list:", classes)

    today = datetime.now().date()
    assignments_list = []

    for class_info in classes:
        class_name = class_info.get('class_name', 'Unknown Class')
        class_type = class_info.get('type')
        course_id = class_info.get('course_id')
        file_id = class_info.get('file_id')

        print(f"Processing class: Name={class_name}, Type={class_type}, Course ID={course_id}, File ID={file_id}")

        if class_type == 'canvas':
            multi_assignment = canvas_api.extract_assignments_content(course_id, access_token)
            assignments = multi_assignment.tasks
            print("Canvas assignments:", assignments)
        elif class_type == 'docx':
            docx_file = canvas_api.get_docx_content(course_id, file_id, access_token)
            multi_assignment = docx_extractor.extract_assignments_from_docx(docx_file)
            assignments = multi_assignment.tasks
            print("DOCX assignments:", assignments)
        elif class_type == 'pdf':
            pdf_file = canvas_api.get_pdf_content(course_id, file_id, access_token)
            multi_assignment = pdf_extractor.extract_assignments_from_pdf(pdf_file)
            assignments = multi_assignment.tasks
            print("PDF assignments:", assignments)
        else:
            continue  # Skip unknown class types

        if not assignments:
            print(f"No assignments found for class '{class_name}'.")
            continue

        for assignment in assignments:
            try:
                print("Processing assignment:", assignment)
                if not assignment.due_date:
                    print(f"Skipping assignment '{assignment.title}' due to missing due date.")
                    continue

                due_date_str = assignment.due_date
                due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00')).date()

                if today <= due_date <= today + timedelta(days=7):
                    assignments_list.append({
                        'class_name': class_name,
                        'title': assignment.title,
                        'due_date': due_date.strftime('%Y-%m-%d'),
                        'description': assignment.description,
                    })
            except Exception as e:
                print(f"Error processing assignment '{assignment}': {e}")
                traceback.print_exc()

    print("Assignments List:", assignments_list)
    return jsonify(assignments_list)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
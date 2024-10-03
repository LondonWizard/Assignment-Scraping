from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta
import canvas_api
import pdf_extractor
import docx_extractor
import json
import os
import traceback

app = Flask(__name__)

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
            multi_assignment = canvas_api.extract_assignments_content(course_id)
            assignments = multi_assignment.tasks
            print("Canvas assignments:", assignments)
        elif class_type == 'docx':
            docx_file = canvas_api.get_docx_content(course_id, file_id)
            multi_assignment = docx_extractor.extract_assignments_from_docx(docx_file)
            assignments = multi_assignment.tasks
            print("DOCX assignments:", assignments)
        elif class_type == 'pdf':
            pdf_file = canvas_api.get_pdf_content(course_id, file_id)
            multi_assignment = pdf_extractor.extract_assignments_from_pdf(pdf_file)
            assignments = multi_assignment.tasks
            print("PDF assignments:", assignments)
        else:
            # print(f"Unknown class type: {class_type}")
            continue  # Properly indented inside the else block

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

# Route to serve the main HTML page
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
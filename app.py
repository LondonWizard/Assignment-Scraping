from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime
import canvas_api
import pdf_extractor
import docx_extractor
from datetime import datetime, timedelta

app = Flask(__name__)
#CORS(app)  # Enable CORS if needed (you might not need this for local use)

# API endpoint to fetch assignments


@app.route('/fetch-assignments', methods=['POST'])
def fetch_assignments():
    data = request.json
    print("Received data: ", data)  # Ensure data is being received
    
    classes = data.get('classes', [])
    print("Classes list: ", classes)  # Check if the classes list is correct

    today = datetime.today().date()
    assignments_list = []

    for class_info in classes:
        class_type = class_info.get('type')
        course_id = class_info.get('course_id')
        file_id = class_info.get('file_id')

        print(f"Processing class: Type={class_type}, Course ID={course_id}, File ID={file_id}")

        if class_type == 'canvas':
            assignments = canvas_api.extract_assignments_content(course_id)
            print("Canvas assignments: ", assignments)
        elif class_type == 'docx':
            docx_file = canvas_api.get_docx_content(course_id, file_id)
            assignments = docx_extractor.extract_assignments_from_docx(docx_file)
            print("DOCX assignments: ", assignments)
        elif class_type == 'pdf':
            pdf_file = canvas_api.get_pdf_content(course_id, file_id)
            assignments = pdf_extractor.extract_assignments_from_pdf(pdf_file)
            print("PDF assignments: ", assignments)

        for assignment in assignments:
            try:
                if not assignment.due_date:
                    print(f"Skipping assignment '{assignment.title}' due to missing due date.")
                    continue
                
                due_date = datetime.fromisoformat(assignment.due_date.replace('Z', '')).date()
                
                if due_date == today or due_date == today + timedelta(days=1):
                    assignments_list.append({
                        'title': assignment.title,
                        'due_date': due_date.strftime('%Y-%m-%d'),
                        'description': assignment.description,
                         })
            except ValueError as e:
                print(f"Error parsing date for assignment {assignment.title}: {e}")

    print("Assignments List: ", assignments_list)
    return jsonify(assignments_list)

# Route to serve the main HTML page
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

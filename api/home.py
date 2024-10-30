from flask import Flask, render_template_string, jsonify, Blueprint, current_app
from utility_services import authenticate
import os

home = Blueprint('home', __name__)  # Define a blueprint for the index or 'homepage' of the application

SCHEMAS = {
    "Milestone_1": [
        {
            "name": "term_start_date",
            "type": "date",
            "description": "Teaching Period Start Date",
            "required": True
        },
        {
            "name": "completion_time",
            "type": "date",
            "description": "Submission Date",
            "required": False
        },
        {
            "name": "email",
            "type": "email",
            "description": "User's email address",
            "required": False
        },
        {
            "name": "name",
            "type": "text",
            "description": "User's full name",
            "required": False
        },
        {
            "name": "subject_coordinator",
            "type": "text",
            "description": "Name of the subject coordinator",
            "required": False
        },
        {
            "name": "subject_code_and_name",
            "type": "text",
            "description": "Subject code and name",
            "required": False
        },
        {
            "name": "subject_lms_link",
            "type": "url",
            "description": "URL to the subject in the Learning Management System",
            "required": False
        },
        {
            "name": "Verify_Assessments_Weightings_2Weeks",
            "type": "checkbox",
            "description": "Verify assessments, weightings, types, and hurdles, to match CourseLoop.",
            "required": False
        },
        {
            "name": "Ensure_LMS_Access_2Weeks",
            "type": "checkbox",
            "description": "Ensure LMS site is setup to allow student access and remove access 12 months after the final grade.",
            "required": False
        },
        {
            "name": "Setup_Welcome_Message_LMS_2Weeks",
            "type": "checkbox",
            "description": "Ensure setup of Welcome message on LMS homepage, with learning materials and the latest Subject Learning Guide.",
            "required": False
        },
        {
            "name": "Add_Teaching_Team_Contact_1Week",
            "type": "checkbox",
            "description": "Add Teaching team contact details, including role, title, portrait, and bios.",
            "required": False
        },
        {
            "name": "Add_Welcome_Post_1Week",
            "type": "checkbox",
            "description": "Add Welcome post to Announcement.",
            "required": False
        },
        {
            "name": "Add_Introduce_Yourself_Post_1Week",
            "type": "checkbox",
            "description": "Add Introduce Yourself Discussion/Padlet post.",
            "required": False
        },
        {
            "name": "Verify_Timetable_Accuracy_By_Week1",
            "type": "checkbox",
            "description": "Verify timetable accuracy in Allocate+ and schedule relevant live online sessions.",
            "required": False
        },
        {
            "name": "Schedule_Student_Consults_By_Week1",
            "type": "checkbox",
            "description": "Schedule live student consults per week, preferably in break time or after hours.",
            "required": False
        },
        {
            "name": "Ensure_First_Assessment_Details_By_Week1",
            "type": "checkbox",
            "description": "Ensure the first assessment details are prepared, including Turnitin enabled submission folders, with grades and rubrics.",
            "required": False
        },
        {
            "name": "Engage_Forums_Respond_2Days_Initial_Weeks",
            "type": "checkbox",
            "description": "Engage regularly on forums and respond to students within 2 business days.",
            "required": False
        },
        {
            "name": "Add_Weekly_Overview_Post_Beginning_Week1",
            "type": "checkbox",
            "description": "Add weekly overview/review post to Announcement, summarizing key points and connecting with upcoming learning.",
            "required": False
        },
        {
            "name": "Upload_Live_Session_Recording_2Days",
            "type": "checkbox",
            "description": "Upload live session recording links to LMS within 2 business days.",
            "required": False
        },
        {
            "name": "post_assignment_reminder",
            "type": "checkbox",
            "description": "Weeks 2 & 3 - Post assessment and support reminder to Announcement a week before due date, where relevant.",
            "required": False
        },
        {
            "name": "accommodate_lap_requirements",
            "type": "checkbox",
            "description": "Weeks 2 & 3 - Accommodate student LAP requirements (e.g., adjusting Quiz/assessment, learning resources, delivery, communications, etc.)",
            "required": False
        },
        {
            "name": "additional_comments",
            "type": "text",
            "description": "Additional comments",
            "required": False
        }
    ],
    "Milestone_2": [
        {
            "name": "term_start_date",
            "type": "date",
            "description": "Teaching Period Start Date",
            "required": True
        },
        {
            "name": "completion_time",
            "type": "date",
            "description": "Submission Date",
            "required": False
        },
        {
            "name": "email",
            "type": "email",
            "description": "User's email address",
            "required": False
        },
        {
            "name": "name",
            "type": "text",
            "description": "User's full name",
            "required": False
        },
        {
            "name": "subject_coordinator",
            "type": "text",
            "description": "Name of the subject coordinator",
            "required": False
        },
        {
            "name": "subject_code_and_name",
            "type": "text",
            "description": "Subject code and name",
            "required": False
        },
        {
            "name": "subject_lms_link",
            "type": "url",
            "description": "URL to the subject in the Learning Management System",
            "required": False
        },
        {
            "name": "respond_in_2_days",
            "type": "checkbox",
            "description": "Weeks 2 & 3 - Engage on forums and respond to students within 2 business days",
            "required": False
        },
        {
            "name": "add_weekly_overview",
            "type": "checkbox",
            "description": "Weeks 2 & 3 - Add weekly overview/review post to Announcement",
            "required": False
        },
        {
            "name": "upload_live_session",
            "type": "checkbox",
            "description": "Weeks 2 & 3 - Upload live session recording links to LMS within 2 business days (1 day for Term subjects)",
            "required": False
        },
        {
            "name": "ensure_lms_materials_ready",
            "type": "checkbox",
            "description": "Weeks 2 & 3 - Ensure LMS materials are ready each week and compliant",
            "required": False
        },
        {
            "name": "ensure_remaining_assessments",
            "type": "checkbox",
            "description": "Weeks 2 & 3 - Ensure assessment details and submission folders are set up",
            "required": False
        },
        {
            "name": "post_assignment_reminder",
            "type": "checkbox",
            "description": "Weeks 2 & 3 - Post assessment and support reminder to Announcement a week before due date, where relevant",
            "required": False
        },
        {
            "name": "accommodate_lap_requirements",
            "type": "checkbox",
            "description": "Weeks 2 & 3 - Accommodate student LAP requirements (e.g., adjusting Quiz/assessment, learning resources, delivery, communications, etc.)",
            "required": False
        },
        {
            "name": "additional_comments",
            "type": "text",
            "description": "Additional comments",
            "required": False
        }
    ],
    "Milestone_3": [
        {
            "name": "term_start_date",
            "type": "date",
            "description": "Teaching Period Start Date",
            "required": True
        },
        {
            "name": "completion_time",
            "type": "date",
            "description": "Submission Date",
            "required": False
        },
        {
            "name": "email",
            "type": "email",
            "description": "User's email address",
            "required": False
        },
        {
            "name": "name",
            "type": "text",
            "description": "User's full name",
            "required": False
        },
        {
            "name": "subject_coordinator",
            "type": "text",
            "description": "Name of the subject coordinator",
            "required": False
        },
        {
            "name": "subject_code_and_name",
            "type": "text",
            "description": "Subject code and name",
            "required": False
        },
        {
            "name": "subject_lms_link",
            "type": "url",
            "description": "URL to the subject in the Learning Management System",
            "required": False
        },
        {
            "name": "Engage_Forums_Respond_2Days_Weeks_4_5_6",
            "type": "checkbox",
            "description": "Engage regularly on forums and respond to students within 2 business days.",
            "required": False
        },
        {
            "name": "Add_Weekly_Overview_Post_Weeks_4_5_6",
            "type": "checkbox",
            "description": "Add weekly overview/review post to Announcement, summarizing key points and connecting with upcoming learning, including live session reminders.",
            "required": False
        },
        {
            "name": "Upload_Live_Session_Recording_2Days_Weeks_4_5_6",
            "type": "checkbox",
            "description": "Upload live session recording links to LMS within 2 business days (1 day for Term subjects).",
            "required": False
        },
        {
            "name": "Ensure_LMS_Materials_Ready_Weeks_4_5_6",
            "type": "checkbox",
            "description": "Ensure remainder of LMS learning materials are ready each week and compliant with copyright.",
            "required": False
        },
        {
            "name": "Ensure_Remaining_Assessments_Weeks_4_5_6",
            "type": "checkbox",
            "description": "Ensure remaining assessment details are available, including Turnitin enabled submission folders, with grades and rubrics.",
            "required": False
        },
        {
            "name": "Post_Assessment_Reminder_Weeks_4_5_6",
            "type": "checkbox",
            "description": "Post assessment and support reminder to Announcement a week before due date, where relevant.",
            "required": False
        },
        {
            "name": "Accommodate_LAP_Requirements_Weeks_4_5_6",
            "type": "checkbox",
            "description": "Accommodate student LAP requirements (e.g., adjusting Quiz/assessment, learning resources, delivery, communications, etc.).",
            "required": False
        },
        {
            "name": "Add_SFS_Survey_Weeks_5_6",
            "type": "checkbox",
            "description": "Add SFS survey to Announcement post and live session presentation slides.",
            "required": False
        },
        {
            "name": "Post_End_Of_Subject_Review_Week_6",
            "type": "checkbox",
            "description": "Post end of subject review and well wishes on Announcement to students.",
            "required": False
        },
        {
            "name": "Hide_LMS_Exam_Grades_Week_6",
            "type": "checkbox",
            "description": "Hide LMS exam grades, final marks, assessment rubrics, grade, and lock discussions at the end of the term.",
            "required": False
        },
        {
            "name": "additional_comments",
            "type": "text",
            "description": "Additional comments",
            "required": False
        }
    ]
}

FORM_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Milestone Report Form</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
            max-width: 900px;  
            margin: auto;
        }
        .container {
            background-color: #fff;
            padding: 40px;  
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-top: 20px;
        }
        h1 {
            font-size: 1.5em;
            margin-bottom: 20px;  
        }
        select, input:not([type="checkbox"]), textarea, button {
            width: 100%;
            margin-top: 10px;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-bottom: 25px; 
            font-size: 1em;
            box-sizing: border-box;  
        }
        label {
            font-weight: 600;
            margin-right: 10px;
            display: block; 
            margin-bottom: 5px;  
        }
        .checkbox-container {
            display: flex;
            align-items: flex-start;
            margin-bottom: 25px;  
            gap: 10px;
        }
        .checkbox-container input[type="checkbox"] {
            flex: 0 0 20px;
            width: 20px;
            height: 20px;
            margin: 3px 0 0 0;
            cursor: pointer;
            -webkit-appearance: none;
            -moz-appearance: none;
            appearance: none;
            border: 2px solid #007BFF;
            border-radius: 4px;
            background-color: white;
            position: relative;
        }
        .checkbox-container input[type="checkbox"]:checked {
            background-color: #007BFF;
        }
        .checkbox-container input[type="checkbox"]:checked::after {
            content: '✓';
            position: absolute;
            color: white;
            font-size: 14px;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
        }
        .checkbox-container label {
            flex: 1;
            font-weight: normal;
            line-height: 1.4;
        }
             button {
            background-color: #007BFF;
            color: white;
            border: none;
            cursor: pointer;
            margin-bottom: 25px;
        }
        button:hover {
            background-color: #0056b3;
        }
        .back-button {
            background-color: transparent;
            color: #666;
            border: 1px solid #ddd;
            padding: 8px 16px;
            font-size: 0.9em;
            width: auto;
            margin-bottom: 20px;
            display: none;  /* Hidden by default */
        }
        .back-button:hover {
            background-color: #f5f5f5;
        }
        .submit-button {
            margin-top: 10px;
        }
        .file-upload {
            margin-top: 30px;  
            padding-top: 30px;  
            border-top: 1px solid #ddd;
            display: block;  
        }
        .file-upload.hidden {  
            display: none;
        }
        .file-upload-label {
            display: block;
            margin-bottom: 15px;  
        }
        #file-name {
            margin-top: 5px;
            font-size: 0.9em;
            color: #666;
        }
        input[type="file"] {
            display: none;
        }
        .custom-file-upload {
            display: inline-block;
            width: calc(100% - 22px);
            padding: 10px;
            background-color: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 5px;
            cursor: pointer;
            text-align: center;
            margin-bottom: 25px; 
        }
        .custom-file-upload:hover {
            background-color: #e9ecef;
        }
        .popup-message {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background-color: rgba(212, 237, 218, 0.98);
            color: #155724;
            border: 2px solid #c3e6cb;
            border-radius: 12px;
            padding: 25px 35px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            display: none;
            z-index: 1000;
            min-width: 300px;
            max-width: 80%;
            text-align: center;
            font-size: 1.2em;
            animation: popup-appear 0.3s ease-out;
        }
        .popup-message.error {
            background-color: rgba(248, 215, 218, 0.98);
            color: #721c24;
            border: 2px solid #f5c6cb;
        }
        .popup-message button {
            position: absolute;
            top: 10px;
            right: 10px;
            background: none;
            border: none;
            font-size: 1.5em;
            cursor: pointer;
            color: inherit;
            padding: 0;
            width: auto;
            height: auto;
        }
        @keyframes popup-appear {
            0% {
                opacity: 0;
                transform: translate(-50%, -40%);
            }
            100% {
                opacity: 1;
                transform: translate(-50%, -50%);
            }
        }
        .popup-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(0, 0, 0, 0.5);
            display: none;
            z-index: 999;
            animation: overlay-appear 0.3s ease-out;
        }
        @keyframes overlay-appear {
            from { opacity: 0; }
            to { opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Milestone Report Form</h1>
        <button id="back-button" class="back-button" onclick="resetToInitialState()">← Back</button>
        
        <label for="academic-period">Academic Period:</label>
        <select id="academic-period" required>
            <option value="Term" selected>Term</option>
            <option value="Semester">Semester</option>
        </select>

        <label for="milestone-select">Select Milestone:</label>
        <select id="milestone-select" required onchange="updateFormFields()">
            <option value="">-- Select Milestone --</option>
            <option value="Milestone_1">Milestone 1</option>
            <option value="Milestone_2">Milestone 2</option>
            <option value="Milestone_3">Milestone 3</option>
        </select>

        <form id="milestone-form" method="POST">
            <div id="form-fields"></div>
            <button type="submit">Submit Form</button>
        </form>

        <div class="file-upload">
            <span class="file-upload-label">Or upload a spreadsheet:</span>
            

            <label for="spreadsheet-academic-period">Academic Period:</label>
            <select id="spreadsheet-academic-period" required>
                <option value="">-- Select Academic Period --</option>
                <option value="Term">Term</option>
                <option value="Semester">Semester</option>
            </select>
            
            <label class="custom-file-upload">
                <input type="file" id="spreadsheet-upload" accept=".xls,.xlsx" onchange="handleFileSelect(event)">
                Click to select Excel file (.xls, .xlsx)
            </label>
            <div id="file-name"></div>
            <button onclick="uploadSpreadsheet()">Upload Spreadsheet</button>
        </div>
    </div>

    <div id="popup-overlay" class="popup-overlay"></div>
    <div id="popup-message" class="popup-message">
        <button onclick="closePopup()">×</button>
        <span id="popup-message-text"></span>
    </div>

    <script>
    const SCHEMAS = {{ schemas | tojson }};

        function updateFormFields() {
            const milestone = document.getElementById('milestone-select').value;
            const formFieldsDiv = document.getElementById('form-fields');
            const fileUploadSection = document.querySelector('.file-upload');
            const backButton = document.getElementById('back-button');
            
            formFieldsDiv.innerHTML = '';  // Clear previous fields

            // Show/hide file upload section based on milestone selection
            if (milestone) {
                fileUploadSection.classList.add('hidden');
                backButton.style.display = 'inline-block';
            } else {
                fileUploadSection.classList.remove('hidden');
                backButton.style.display = 'none';
            }

            if (milestone && SCHEMAS[milestone]) {
                SCHEMAS[milestone].forEach(field => {
                    let inputElement;

                    if (field.type === 'checkbox') {
                        inputElement = `
                            <div class="checkbox-container">
                                <input type="checkbox" id="${field.name}" name="${field.name}" value="true">
                                <label for="${field.name}">${field.description}</label>
                            </div>`;
                    } else {
                        inputElement = `
                            <label for="${field.name}">${field.description}</label>
                            <input type="${field.type}" id="${field.name}" name="${field.name}" ${field.required ? 'required' : ''}>
                        `;
                    }

                    formFieldsDiv.innerHTML += inputElement;
                });
            }
        }

        document.getElementById('milestone-form').addEventListener('submit', async function (event) {
            event.preventDefault();

            const jsonData = {};
            
            jsonData.milestone = document.getElementById('milestone-select').value;
            jsonData.academic_period = document.getElementById('academic-period').value;
            const formElements = event.target.elements;
            
            for (let element of formElements) {
                if (element.type === 'checkbox') {
                    jsonData[element.name] = element.checked;
                } else if (element.name && element.type !== 'submit') {
                    jsonData[element.name] = element.value;
                }
            }

            try {
                const tokenResponse = await fetch('/api/get_auth_token');
                if (!tokenResponse.ok) {
                    throw new Error('Failed to authenticate.');
                }
                const { auth_token } = await tokenResponse.json();

                const pocketbaseUrl = "{{ pocketbase_url }}/api/collections/" + jsonData.milestone + "/records";

                const response = await fetch(pocketbaseUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': auth_token
                    },
                    body: JSON.stringify(jsonData)
                });

                const data = await response.json();

                if (response.ok) {
                    showPopup('Form submitted successfully!', false);
                    resetForm();
                } else {
                    showPopup(data.error || 'There was an error submitting the form.', true);
                }
            } catch (error) {
                console.error('Error:', error);
                showPopup('There was an error submitting the form.', true);
            }
        });
        function handleFileSelect(event) {
            const file = event.target.files[0];
            if (file) {
                document.getElementById('file-name').textContent = `Selected file: ${file.name}`;
            }
        }

        async function uploadSpreadsheet() {
            const fileInput = document.getElementById('spreadsheet-upload');
            const academicPeriod = document.getElementById('spreadsheet-academic-period').value;
            const file = fileInput.files[0];
            
            if (!file) {
                showPopup('Please select a file first.', true);
                return;
            }

            if (!academicPeriod) {
                showPopup('Please select an academic period first.', true);
                return;
            }

            try {
                const tokenResponse = await fetch('/api/get_auth_token');
                if (!tokenResponse.ok) {
                    throw new Error('Failed to authenticate.');
                }
                const { auth_token } = await tokenResponse.json();

                const formData = new FormData();
                formData.append('file', file);

                const response = await fetch(`/api/add_spreadsheet?${academicPeriod}`, {
                    method: 'POST',
                    headers: {
                        'Authorization': auth_token
                    },
                    body: formData
                });

                if (response.ok) {
                    showPopup('Spreadsheet uploaded successfully!', false);
                    fileInput.value = '';
                    document.getElementById('file-name').textContent = '';
                    document.getElementById('spreadsheet-academic-period').value = '';
                } else {
                    const error = await response.json();
                    showPopup(error.message || 'Error uploading spreadsheet.', true);
                }
            } catch (error) {
                console.error('Error:', error);
                showPopup('Error uploading spreadsheet.', true);
            }
        }

        function showPopup(message, isError = false) {
            const popup = document.getElementById('popup-message');
            const overlay = document.getElementById('popup-overlay');
            const popupText = document.getElementById('popup-message-text');
            popupText.textContent = message;
            popup.classList.toggle('error', isError);
            popup.style.display = 'block';
            overlay.style.display = 'block';

            setTimeout(() => {
                closePopup();
            }, 5000);
        }

        function closePopup() {
            const popup = document.getElementById('popup-message');
            const overlay = document.getElementById('popup-overlay');
            popup.style.display = 'none';
            overlay.style.display = 'none';
        }

           function resetToInitialState() {
            const form = document.getElementById('milestone-form');
            const formFieldsDiv = document.getElementById('form-fields');
            const fileUploadSection = document.querySelector('.file-upload');
            const backButton = document.getElementById('back-button');
            const milestoneSelect = document.getElementById('milestone-select');
            
            // Reset form and clear fields
            form.reset();
            formFieldsDiv.innerHTML = '';
            
            // Reset milestone select
            milestoneSelect.value = '';
            
            // Show file upload section and hide back button
            fileUploadSection.classList.remove('hidden');
            backButton.style.display = 'none';
            
            // Reset file upload section
            const fileInput = document.getElementById('spreadsheet-upload');
            if (fileInput) {
                fileInput.value = '';
                document.getElementById('file-name').textContent = '';
            }
            const spreadsheetAcademicPeriod = document.getElementById('spreadsheet-academic-period');
            if (spreadsheetAcademicPeriod) {
                spreadsheetAcademicPeriod.value = '';
            }
        }

        function resetForm() {
            resetToInitialState();  // Use the same function for consistency
        }

        document.getElementById('milestone-form').addEventListener('submit', async function (event) {
            event.preventDefault();

     
            const jsonData = {};
            
      
            jsonData.milestone = document.getElementById('milestone-select').value;
            jsonData.academic_period = document.getElementById('academic-period').value;


            const formElements = event.target.elements;
            
            for (let element of formElements) {
                if (element.type === 'checkbox') {
                    // For checkboxes, explicitly set boolean value
                    jsonData[element.name] = element.checked;
                } else if (element.name && element.type !== 'submit') {
                    // For other inputs, use their value
                    jsonData[element.name] = element.value;
                }
            }

            try {
                const tokenResponse = await fetch('/api/get_auth_token');
                if (!tokenResponse.ok) {
                    throw new Error('Failed to authenticate.');
                }
                const { auth_token } = await tokenResponse.json();

                const pocketbaseUrl = "{{ pocketbase_url }}/api/collections/" + jsonData.milestone + "/records";

                const response = await fetch(pocketbaseUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': auth_token
                    },
                    body: JSON.stringify(jsonData)
                });

                const data = await response.json();

                if (response.ok) {
                    showPopup('Form submitted successfully!', false);
                    resetToInitialState();  
                } else {
                    showPopup(data.error || 'There was an error submitting the form.', true);
                }
            } catch (error) {
                console.error('Error:', error);
                showPopup('There was an error submitting the form.', true);
            }
        });
    </script>
</body>
</html>
"""

@home.route('/', methods=['GET'])
def milestone_form():
    pocketbase_url = os.getenv('POCKETBASE_URL')
    return render_template_string(FORM_TEMPLATE, schemas=SCHEMAS, pocketbase_url=pocketbase_url)

@home.route('/api/get_auth_token', methods=['GET'])
def get_auth_token():
    try:
        # Get the auth token using the Python function
        auth_token = authenticate()
        if not auth_token:
            return jsonify({'error': 'Failed to authenticate.'}), 401

        # Return the auth token as JSON
        return jsonify({'auth_token': auth_token})
    except Exception as e:
        current_app.logger.exception("Error getting auth token.")
        return jsonify({'error': str(e)}), 500

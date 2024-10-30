import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import datetime, timedelta
from unittest.mock import patch
from io import BytesIO
import pandas as pd
import requests
from app import app
from flask import json
import unittest

class SpreadSheet_Tests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()  # This pushes the application context
        self.base_url = os.getenv('POCKETBASE_URL')
        if not self.base_url:
            raise ValueError("POCKETBASE_URL environment variable is not set")
        self.admin_email = os.getenv('POCKETBASE_ADMIN_EMAIL')
        if not self.admin_email:
            raise ValueError(
                "POCKETBASE_ADMIN_EMAIL environment variable is not set")
        self.admin_password = os.getenv('POCKETBASE_ADMIN_PASSWORD')
        if not self.admin_password:
            raise ValueError(
                "POCKETBASE_ADMIN_PASSWORD environment variable is not set")
        auth_data = {
            "identity": self.admin_email,
            "password": self.admin_password
        }
        auth_response = requests.post(
            f"{self.base_url}/api/admins/auth-with-password", json=auth_data)
        auth_response.raise_for_status()
        self.admin_token = auth_response.json()["token"]
        self.headers = {
            "Authorization": f"{self.admin_token}"
        }

    @patch('date.get_AEST_date')
    def test_upload_and_download_spreadsheet(self, mock_get_AEST_date):
        term_start_date = datetime(2024, 10, 14)
        mock_current_date = term_start_date + timedelta(days=10)  # Milestone 1
        mock_get_AEST_date.return_value = mock_current_date.date()
        completion_time = datetime.now().isoformat()
        # Create excel file to upload
        data = {
            # Start date of the teaching period
            'term_start_date': term_start_date.strftime("%Y-%m-%d"),
            'completion_time': [completion_time],  # Autofilled completion time
            'email': ['test-user@example.com'],  # User's email address
            'name': ['John Doe'],  # User's full name
            # Subject coordinator's name
            'subject_coordinator': ['Dr. Jane Smith'],
            # Subject code and name
            'subject_code_and_name': ['COMP101 - Introduction to Computing'],
            # LMS link
            'subject_lms_link': ['https://lms.example.com/subjects/COMP101'],
            # Boolean fields for Milestone 1 tasks
            'Verify_Assessments_Weightings_2Weeks': [True],
            'Ensure_LMS_Access_2Weeks': [True],
            'Setup_Welcome_Message_LMS_2Weeks': [False],
            'Add_Teaching_Team_Contact_1Week': [True],
            'Add_Welcome_Post_1Week': [True],
            'Add_Introduce_Yourself_Post_1Week': [True],
            'Verify_Timetable_Accuracy_By_Week1': [False],
            'Schedule_Student_Consults_By_Week1': [True],
            'Ensure_First_Assessment_Details_By_Week1': [True],
            'Engage_Forums_Respond_2Days_Initial_Weeks': [True],
            'Add_Weekly_Overview_Post_Beginning_Week1': [True],
            'Upload_Live_Session_Recording_2Days': [False],
            'post_assignment_reminder': [True],
            'accommodate_lap_requirements': [False],
            # Additional comments
            'additional_comments': ['Everything is on track for the first weeks.']
        }
        df = pd.DataFrame(data)
        excel_file = BytesIO()
        with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        excel_file.seek(0)
        # Simulate file upload
        data = {
            'file': (excel_file, 'test.xlsx')
        }
        response = self.app.post('/api/add_spreadsheet', data=data,
                                 content_type='multipart/form-data', headers=self.headers)
        # Check response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIn("message", response_data)
        self.assertEqual(
            response_data["message"], "Spreadsheet parsed and record created successfully")
        record_id = response_data.get("record_id")
        # Fetch the records from PocketBase
        records_response = self.app.get(
            f'/api/get_record/{record_id}',
            headers=self.headers,
            query_string={'term_start_date': term_start_date.isoformat()}
        )
        self.assertEqual(records_response.status_code, 200)
        export_response = self.app.get(
            f'/api/get_spreadsheet/{record_id}',
            headers=self.headers,
            query_string={'term_start_date': term_start_date.isoformat()}
        )
        # Check export response
        self.assertEqual(export_response.status_code, 200)
        self.assertEqual(export_response.headers['Content-Type'],
                         'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')



if __name__ == '__main__':
    unittest.main()

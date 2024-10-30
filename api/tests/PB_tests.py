import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import random
from unittest.mock import patch
from date import determine_form
from datetime import datetime, timedelta
import requests
import json
from app import app
import unittest




def random_bool():
    return random.choice([True, False])


class PocketBaseTests(unittest.TestCase):
    # Test suite for core functionality using PB
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
            "Content-Type": "application/json",
            "Authorization": f"Admin {self.admin_token}"
        }

    @patch('date.get_AEST_date')
    def test_milestone_1(self, mock_get_AEST_date):
        term_start_date = datetime(2024, 10, 14)  
        mock_current_date = term_start_date + timedelta(days=1) # Within Milestone 1
        mock_get_AEST_date.return_value = mock_current_date.date()

        test_data = {
            "term_start_date": term_start_date.strftime("%Y-%m-%d"),
            "current_date": mock_current_date.strftime("%Y-%m-%d"),
            "start_time": datetime.now().isoformat(),
            "completion_time": datetime.now().isoformat(),
            "email": "test-user@example.com",  
            "name": "John Doe",  
            "subject_coordinator": "Dr. Jane Smith", 
            "subject_code_and_name": "COMP101 - Introduction to Computing",  
            "subject_lms_link": "https://lms.example.com/subjects/COMP101", 
            "Verify_Assessments_Weightings_2Weeks": random_bool(),
            "Ensure_LMS_Access_2Weeks": random_bool(),
            "Setup_Welcome_Message_LMS_2Weeks": random_bool(),
            "Add_Teaching_Team_Contact_1Week": random_bool(),
            "Add_Welcome_Post_1Week": random_bool(),
            "Add_Introduce_Yourself_Post_1Week": random_bool(),
            "Verify_Timetable_Accuracy_By_Week1": random_bool(),
            "Schedule_Student_Consults_By_Week1": random_bool(),
            "Ensure_First_Assessment_Details_By_Week1": random_bool(),
            "Engage_Forums_Respond_2Days_Initial_Weeks": random_bool(),
            "Add_Weekly_Overview_Post_Beginning_Week1": random_bool(),
            "Upload_Live_Session_Recording_2Days": random_bool(),
            "post_assignment_reminder": random_bool(),
            "accommodate_lap_requirements": random_bool(),
            "additional_comments": "Everything is on track for the first weeks."
        }
        response = self.app.post(
            '/api/submit_form',
            data=json.dumps(test_data),
            content_type='application/json',
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIn("message", response_data)
        self.assertEqual(response_data["message"],
                         "Form submission successful")

        records_response = requests.get(
            f"{self.base_url}/api/collections/{determine_form(term_start_date)}/records",
            headers={"Authorization": self.admin_token}
        )
        self.assertEqual(records_response.status_code, 200)

    @patch('date.get_AEST_date')
    def test_milestone_2(self, mock_get_AEST_date):
        term_start_date = datetime(2024, 9, 10)  
        mock_current_date = term_start_date + timedelta(days=10) # Within Milestone 2
        mock_get_AEST_date.return_value = mock_current_date.date()

        test_data = {
            "term_start_date": term_start_date.strftime("%Y-%m-%d"),
            "current_date": mock_current_date.strftime("%Y-%m-%d"),
            "completion_time": datetime.now().isoformat(),  
            "email": "newexmaple@example.com",  
            "name": "John Doe",  
            "subject_coordinator": "Dr. Jane Smith", 
            "subject_code_and_name": "COMP2024 - Advanced Computing", 
            "subject_lms_link": "https://lms.example.com/subjects/COMP2024", 
            "respond_in_2_days": random_bool(),
            "add_weekly_overview": random_bool(),
            "upload_live_session": random_bool(),
            "ensure_lms_materials_ready": random_bool(),  
            "ensure_remaining_assessments": random_bool(), 
            "post_assignment_reminder": random_bool(),
            "accommodate_lap_requirements": random_bool(),
            "additional_comments": "No additional comments at this time." 

        }
        response = self.app.post(
            '/api/submit_form',
            data=json.dumps(test_data),
            content_type='application/json',
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIn("message", response_data)
        self.assertEqual(response_data["message"],
                         "Form submission successful")

        records_response = requests.get(
            f"{self.base_url}/api/collections/{determine_form(term_start_date)}/records",
            headers={"Authorization": self.admin_token}
        )
        self.assertEqual(records_response.status_code, 200)
        response_data = json.loads(response.data)
    @patch('date.get_AEST_date')
    def test_milestone_3_and_update_api(self, mock_get_AEST_date):
        term_start_date = datetime(2024, 9, 10)  
        mock_current_date = term_start_date + timedelta(days=21) # Within Milestone 3
        mock_get_AEST_date.return_value = mock_current_date.date()
        test_data = {
            "term_start_date": term_start_date.strftime("%Y-%m-%d"),
            "current_date": mock_current_date.strftime("%Y-%m-%d"),
            "start_time": datetime.now().isoformat(),
            "completion_time": datetime.now().isoformat(),
            "email": "test@example.com",
            "name": "Test User",
            "subject_coordinator": "Coordinator Name",
            "subject_code_and_name": "SUBJ1001 - Test Subject",
            "subject_lms_link": "http://example.com/lms",
            "respond_in_2_days": random_bool(),
            "add_weekly_overview": random_bool(),
            "upload_live_session": random_bool(),
            "ensure_lms_materials_ready": random_bool(),
            "ensure_remaining_assessments": random_bool(),
            "post_assignment_reminder": random_bool(),
            "accommodate_lap_requirements": random_bool(),
            "additional_comments": "No comments",
            "Engage_Forums_Respond_2Days_Weeks_4_5_6": random_bool(),
            "Add_Weekly_Overview_Post_Weeks_4_5_6": random_bool(),
            "Upload_Live_Session_Recording_2Days_Weeks_4_5_6": random_bool(),
            "Ensure_LMS_Materials_Ready_Weeks_4_5_6": random_bool(),
            "Ensure_Remaining_Assessments_Weeks_4_5_6": random_bool(),
            "Post_Assessment_Reminder_Weeks_4_5_6": random_bool(),
            "Accommodate_LAP_Requirements_Weeks_4_5_6": random_bool(),
            "Add_SFS_Survey_Weeks_5_6": random_bool(),
            "Post_End_Of_Subject_Review_Week_6": random_bool(),
            "Hide_LMS_Exam_Grades_Week_6": random_bool()
        }

        response = self.app.post(
            '/api/submit_form',
            data=json.dumps(test_data),
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        record_id = response_data.get("record_id")
        # Test get_logic
        get_response = self.app.get(
            f'/api/get_record/{record_id}',
            headers=self.headers,
            query_string={'term_start_date': term_start_date.isoformat()}
        )
        self.assertEqual(get_response.status_code, 200)
        retrieved_record = json.loads(get_response.data)
        self.assertEqual(retrieved_record["record_id"], record_id)
        # Test update_logic
        updated_data = {
            "additional_comments": "Updated comments."
        }
        update_response = self.app.patch(
            f'/api/update_record/{record_id}',
            data=json.dumps(updated_data),
            headers=self.headers,
            query_string={'term_start_date': term_start_date.isoformat()}
        )
        self.assertEqual(update_response.status_code, 200)
        updated_record = json.loads(update_response.data)
        self.assertEqual(
            updated_record["additional_comments"], "Updated comments.")
    @patch('date.get_AEST_date')

    def test_delete_route(self, mock_get_AEST_date):
        term_start_date = datetime(2024, 9, 10)  
        mock_current_date = term_start_date + timedelta(days=10)
        mock_get_AEST_date.return_value = mock_current_date.date()
        test_data = {
            "term_start_date": term_start_date.strftime("%Y-%m-%d"),
            "current_date": mock_current_date.strftime("%Y-%m-%d"),
            "completion_time": datetime.now().isoformat(), 
            "email": "newexmaple@example.com", 
            "name": "John Doe",  
            "subject_coordinator": "Dr. Jane Smith",  
            "subject_code_and_name": "COMP2024 - Advanced Computing",  
            "subject_lms_link": "https://lms.example.com/subjects/COMP2024", 
            "respond_in_2_days": random_bool(),
            "add_weekly_overview": random_bool(),
            "upload_live_session": random_bool(), 
            "ensure_lms_materials_ready": random_bool(),  
            "ensure_remaining_assessments": random_bool(),
            "post_assignment_reminder": random_bool(),
            "accommodate_lap_requirements": random_bool(),
            "additional_comments": "No additional comments at this time." 
        }
        response = self.app.post(
            '/api/submit_form',
            data=json.dumps(test_data),
            content_type='application/json',
            headers=self.headers

        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIn("message", response_data)
        self.assertEqual(response_data["message"],
                         "Form submission successful")
        records_response = requests.get(
            f"{self.base_url}/api/collections/{determine_form(term_start_date)}/records",
            headers={"Authorization": self.admin_token}

        )
        self.assertEqual(records_response.status_code, 200)
        response_data = json.loads(response.data)
        record_id = response_data.get("record_id")
        delete_response = self.app.delete(
            f'/api/delete_record/{record_id}',
            headers=self.headers,
            query_string={'term_start_date': term_start_date.isoformat()}
        )
        self.assertEqual(delete_response.status_code, 204)
        
if __name__ == "__main__":
    unittest.main()

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # This needs to be before other imports.
import unittest
from unittest.mock import patch
import json
import requests
from datetime import datetime, timedelta
from app import app
from utility_services import authenticate
from metrics import get_user_metrics
from gemini import get_course_improvement_ideas
from date import determine_form
import random



def random_bool():
    return random.choice([True, False])


class Metric_Tests(unittest.TestCase):
    # Test suite for core functionality using PocketBase

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
    def test_get_user_metrics(self, mock_get_AEST_date):
        term_start_date = datetime(2024, 10, 14)
        # Mock current date to be 10 days after term start
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
        test_mail = 'newexmaple@example.com'
        # Call get_user_metrics with the test email
        user_metrics = get_user_metrics(test_mail)

        # Check that user_metrics['email'] == test_email
        self.assertEqual(user_metrics['email'], test_mail)


        # delete the record
        collection_name = f"{determine_form(term_start_date)}"
        new_response = requests.get(
            f"{self.base_url}/api/collections/{collection_name}/records",
            headers={"Authorization": f"{self.admin_token}"}
        )
        response_data = new_response.json()
        record_id = response_data.get("items", [])[0].get("id")
        delete_response = self.app.delete(
            f'/api/delete_record/{record_id}',
            headers=self.headers,
            query_string={'term_start_date': term_start_date.isoformat()}
        )
        self.assertEqual(delete_response.status_code, 204)

    class TestGeminiIntegration(unittest.TestCase):
        def setUp(self):

            self.base_url = os.getenv('POCKETBASE_URL')
            self.app = app.test_client()
            self.ctx = app.app_context()
            self.ctx.push()
            if not self.base_url:
                raise ValueError(
                    "POCKETBASE_URL environment variable is not set")
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
            admin_token = self.admin_token


            self.headers = {
                "Content-Type": "application/json",
                "Authorization": authenticate(),
            }

    @patch('date.get_AEST_date')
    def test_gemini_integration(self, mock_get_AEST_date):

        term_start_date = datetime(2024, 10, 14)
        # Mock current date to be 10 days after term start
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
        record_id = response_data.get("record_id")
        ideas = get_course_improvement_ideas(test_data['email'])
        self.assertIsNotNone(ideas)
        self.assertGreater(len(ideas), 0)
        # print("Generated improvement ideas:")
        # for idea in ideas:
        #     print(f"- {idea}")
        # # delete generated record
        delete_response = self.app.delete(
            f'/api/delete_record/{record_id}',
            headers=self.headers,
            query_string={'term_start_date': term_start_date.isoformat()}

        )
        self.assertEqual(delete_response.status_code, 204)

if __name__ == "__main__":
    unittest.main()

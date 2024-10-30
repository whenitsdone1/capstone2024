import sys
import os
# Testing files need to be mounted to the main dir to prevent access issues.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from app import app
import json
import requests
from datetime import datetime, timedelta
from date import determine_form, get_AEST_date
import random



def random_bool():  # Generate random answers for testing
    return random.choice([True, False])


class AdminBlueprintTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()  # Push application context for logging
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

        # Authenticate admin and get the token
        auth_data = {
            "identity": self.admin_email,
            "password": self.admin_password
        }
        auth_response = requests.post(
            f"{self.base_url}/api/admins/auth-with-password", json=auth_data)
        auth_response.raise_for_status()
        self.admin_token = auth_response.json()["token"]

        self.headers = {
            "Authorization": f"Admin {self.admin_token}"
        }

    def test_admin_get_all_records(self):
        """Test fetching all records from all collections."""
        response = self.app.get('/admin/records', headers=self.headers)
        self.assertEqual(response.status_code, 200)

        # Verify that the response contains records
        records = json.loads(response.data)
        self.assertIsInstance(records, list)
        self.assertGreater(len(records), 0)

        # Check that each record contains required fields
        for record in records:
            self.assertIn('id', record)
            self.assertIn('email', record)
            self.assertIn('milestone', record)
            self.assertIn('submission_date', record)

    def test_admin_get_specific_record(self):
        """Test fetching a specific record by ID."""
        # Create a test record first
        term_start_date = get_AEST_date() - timedelta(days=10)
        milestone = determine_form(term_start_date)
        collection_name = f"{milestone}"

        # Create a test record in PocketBase

        test_data = {
            "term_start_date": term_start_date.strftime("%Y-%m-%d"),
            "current_date": get_AEST_date().strftime("%Y-%m-%d"),
            "completion_time": datetime.now().isoformat(),  # Completion time of the milestone
            "email": "newexmaple@example.com",  # User's email address
            "name": "John Doe",  # User's full name
            "subject_coordinator": "Dr. Jane Smith",  # Name of the subject coordinator
            "subject_code_and_name": "COMP2024 - Advanced Computing",  # Subject code and name
            "subject_lms_link": "https://lms.example.com/subjects/COMP2024",  # LMS subject link

            # Boolean fields for Milestone 2 tasks
            # Engage on forums and respond within 2 business days
            "respond_in_2_days": random_bool(),
            # Add weekly overview post to announcements
            "add_weekly_overview": random_bool(),
            "upload_live_session": random_bool(),  # Upload live session recording links
            "ensure_lms_materials_ready": random_bool(),  # Ensure LMS materials are ready
            "ensure_remaining_assessments": random_bool(),  # Ensure assessments are set up
            # Post assignment and support reminder
            "post_assignment_reminder": random_bool(),
            # Accommodate student LAP requirements
            "accommodate_lap_requirements": random_bool(),

            # Additional comments
            "additional_comments": "No additional comments at this time."  # Optional comments
        }

        response = self.app.post(
            '/api/submit_form',
            data=json.dumps(test_data),
            content_type='application/json',
            headers=self.headers
        )
        self.assertIn(response.status_code, [200, 201])
        record = json.loads(response.data)
        id = record.get("record_id")
        # Fetch the record via the admin route
        response = self.app.get(f'/admin/records/{id}', headers=self.headers)
        self.assertEqual(response.status_code, 200)

        # Verify the data in the record
        record_data = json.loads(response.data)
        self.assertIn('id', record_data)
        self.assertIn('email', record_data)
        self.assertEqual(record_data['id'], id)

        # Clean up: delete the created record
        delete_response = requests.delete(
            f"{self.base_url}/api/collections/{collection_name}/records/{id}",  
            headers={"Authorization": f"{self.admin_token}"}
        )
        self.assertIn(delete_response.status_code, [200, 204])

    def test_admin_get_record_not_found(self):
        """Test fetching a record with a non-existent ID."""
        non_existent_record_id = "non_existent_id_12345"
        response = self.app.get(
            f'/admin/records/{non_existent_record_id}', headers=self.headers)
        self.assertEqual(response.status_code, 404)

        # Verify that the error message is returned
        error_data = json.loads(response.data)
        self.assertIn('error', error_data)
        self.assertEqual(error_data['error'], 'Record not found')


if __name__ == '__main__':
    unittest.main()

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # This needs to sit before other imports
import unittest
import requests
import json
from datetime import datetime, timedelta
from unittest.mock import patch
from googleapiclient.discovery import build
from mail import send_email, authenticate_gmail
from date import get_AEST_date
from app import app



class TestMailSending(unittest.TestCase):

    @patch('date.determine_form')
    def setUp(self, mock_determine_form):
        mock_determine_form.return_value = "Milestone_1"

        # Set up Flask test client and application context
        self.app = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()
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
            f"{self.base_url}/api/admins/auth-with-password", json=auth_data
        )
        auth_response.raise_for_status()
        self.admin_token = auth_response.json()["token"]

      
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": self.admin_token
        }


        self.test_email = os.getenv('TEST_EMAIL')
        self.term_start_date = get_AEST_date() - timedelta(days=10)  # Within Milestone 2

        test_data = {
            "term_start_date": self.term_start_date.strftime("%Y-%m-%d"),
            "current_date": get_AEST_date().strftime("%Y-%m-%d"),
            "start_time": datetime.now().isoformat(),
            "completion_time": datetime.now().isoformat(),
            "email": self.test_email,
            "name": "Test User",
            "subject_coordinator": "Coordinator Name",
            "subject_code_and_name": "SUBJ1001 - Test Subject",
            "subject_lms_link": "http://example.com/lms",
            "respond_in_2_days": True,
            "add_weekly_overview": True,
            "upload_live_session": False,
            "ensure_lms_materials_ready": True,
            "ensure_remaining_assessments": False,
            "post_assignment_reminder": True,
            "accommodate_lap_requirements": False,
            "additional_comments": "No comments",
            "Engage_Forums_Respond_2Days_Weeks_4_5_6": True,
            "Add_Weekly_Overview_Post_Weeks_4_5_6": True,
            "Upload_Live_Session_Recording_2Days_Weeks_4_5_6": False,
            "Ensure_LMS_Materials_Ready_Weeks_4_5_6": True,
            "Ensure_Remaining_Assessments_Weeks_4_5_6": False,
            "Post_Assessment_Reminder_Weeks_4_5_6": True,
            "Accommodate_LAP_Requirements_Weeks_4_5_6": False,
            "Add_SFS_Survey_Weeks_5_6": True,
            "Post_End_Of_Subject_Review_Week_6": True,
            "Hide_LMS_Exam_Grades_Week_6": False
        }

        # Submit the form
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

    def test_send_milestone_email(self):
        """Test the actual sending of an email."""

        creds = authenticate_gmail()
        service = build('gmail', 'v1', credentials=creds)

       
        sender = self.test_email
        subject = "Reporting For Milestone 1"
        body = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Milestone 1 Reporting</title>
  </head>
  <body style="font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 0;">
    <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f4f4f4; padding: 20px;">
      <tr>
        <td align="center">
          <table role="presentation" style="max-width: 600px; width: 100%; background-color: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <tr>
              <td style="padding: 10px 0; text-align: center; font-size: 24px; font-weight: bold; color: #333;">
                Milestone 1 Reporting Required
              </td>
            </tr>
            <tr>
              <td style="padding: 10px 0 20px 0; text-align: left; font-size: 16px; color: #555;">
                Dear Instructor,
              </td>
            </tr>
            <tr>
              <td style="padding: 10px 0 20px 0; text-align: left; font-size: 16px; color: #555;">
                This is a friendly reminder to log in to the system and complete the <strong>Milestone 1 reporting</strong> at your earliest convenience. Your timely submission ensures everything stays on track for the start of the term.
              </td>
            </tr>
            <tr>
              <td style="padding: 10px 0; text-align: left; font-size: 16px; color: #555;">
                <strong>Access the system here:</strong> <a href="https://www.latrobe.edu.au/" style="color: #1a73e8;">Click here to log in</a>
              </td>
            </tr>
            <tr>
              <td style="padding: 20px 0 10px 0; text-align: left; font-size: 16px; color: #555;">
                If you have any questions or need further assistance, please feel free to reach out.
              </td>
            </tr>
            <tr>
              <td style="padding: 20px 0; text-align: left; font-size: 16px; color: #555;">
                Thank you for your prompt attention!
              </td>
            </tr>
            <tr>
              <td style="padding: 10px 0; text-align: left; font-size: 16px; color: #555;">
                Best regards,<br>
                <strong>La Trobe CSIT QA</strong><br>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
"""
        try:
            # Send the email to the test email address
            send_email(
                service=service,
                sender=sender,
                recipient=self.test_email,
                subject=subject,
                body=body
            )
          #  print(f"An email should have been sent to {self.test_email}")
        except Exception as e:
            self.fail(f"send_email raised an exception: {e}")


if __name__ == '__main__':
    unittest.main()

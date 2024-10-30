from typing import Dict
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
import os
import base64
import json
from utility_services import get_url
from pocketbase import PocketBase
from flask import current_app

# Initialize PocketBase
pb = PocketBase(get_url())

# Gmail API Scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def authenticate_gmail() -> Credentials:
    """
    Authenticates using OAuth 2.0 and returns Gmail API credentials.
    If token.json is missing or invalid, it prompts the user to authenticate via the console.
    """
    creds = None

    # Check if token.json exists and load it
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        except ValueError:
            print("Invalid token.json format. Re-authenticating...")

    # If no valid credentials, perform the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES,
                redirect_uri='urn:ietf:wg:oauth:2.0:oob'
            )

            # Run local server and print the URL for manual authentication
            auth_url, _ = flow.authorization_url(
                prompt='consent')  # Unpack tuple
            print(
                f"Please visit this URL to authorize this application: {auth_url}")

            code = input("Enter the authorization code: ")
            flow.fetch_token(code=code)
            creds = flow.credentials  # Get the Credentials object

        # Save credentials
        token_data = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes
        }
        # Save the new credentials to token.json
        with open('token.json', 'w') as token:
            json.dump(token_data, token)
    return creds


def create_message(sender: str, recipient: str, subject: str, body: str) -> Dict[str, str]:
    message = MIMEText(body, 'html')
    message['to'] = recipient
    message['from'] = sender
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}


def send_email(service, sender: str, recipient: str, subject: str, body: str) -> None:
    try:
        message = create_message(sender, recipient, subject, body)
        sent_message = service.users().messages().send(
            userId='me', body=message).execute()
        print(f"Email sent to {recipient}. Message ID: {sent_message['id']}")
    except Exception as e:
        current_app.logger.warning(f"Failed to send email to {recipient} {e}")
       

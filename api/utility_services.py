import logging
import os
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
import requests
from flask import current_app
from typing import Union, Optional, Dict, Any


load_dotenv("secrets.env")

# Set environment variables
POCKETBASE_URL = os.getenv("POCKETBASE_URL")
ADMIN_EMAIL: Optional[str] = os.getenv("POCKETBASE_ADMIN_EMAIL")
ADMIN_PASSWORD: Optional[str] = os.getenv("POCKETBASE_ADMIN_PASSWORD")

_auth_logged = False


def setup_logging(app: any, created_file=False) -> None:
    """
    Set up logging for the application.
    """
    logs_path = os.path.abspath('logs.txt')
    if not os.path.exists(logs_path):
        created_file = True
        open('logs.txt', 'a').close()

    handler: RotatingFileHandler = RotatingFileHandler(
        'logs.txt', maxBytes=100000, backupCount=1)
    handler.setLevel(logging.INFO)
    formatter: logging.Formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s'
    )
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    if created_file:
        app.logger.info(
            f"Log file not found. Created new log file at: {logs_path}")
    else:
        app.logger.info(f"Existing log file found at: {logs_path}")

def get_url() -> Optional[str]:
    """
    Get the PocketBase URL from environment variables.
    """
    url: Optional[str] = POCKETBASE_URL
    if not url:
        raise ValueError("URL was not correctly retrieved.")
    return url if url else current_app.logger.error("Failed to retrieve PocketBase URL")

def authenticate() -> Union[str, None]:
    """
    Authenticate with PocketBase and return the admin token.
    """
    global _auth_logged

    if not ADMIN_EMAIL or not ADMIN_PASSWORD or not POCKETBASE_URL:
        current_app.logger.exception(
            "Admin email, password, or PocketBase URL not set in environment variables.")
        return None
    auth_data: Dict[str, str] = {
        "identity": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    headers: Dict[str, str] = {'Content-Type': 'application/json'}
    auth_response: requests.Response = requests.post(
        f"{POCKETBASE_URL}/api/admins/auth-with-password",
        json=auth_data,
        headers=headers
    )
    if auth_response.status_code == 200:
        token: Optional[str] = auth_response.json().get("token")
        if token:
            if not _auth_logged:
                current_app.logger.info(
                    "Successfully authenticated with PocketBase.")
                _auth_logged = True
            return token
        else:
            current_app.logger.critical(
                f"Authentication failed, no token in response: {auth_response.text}")
            return None
    else:
        current_app.logger.critical(
            f"Authentication failed with status code {auth_response.status_code}: {auth_response.text}")
        return None


def initialize_collections() -> None:
    from db_schema import SCHEMAS
    # this needs to be here to prevent circular imports
    from db_util import create_or_update_pocketbase_collection
    """
    Initialize collections in PocketBase based on defined schemas.
    """


    for milestone in SCHEMAS.keys():
        collection_name: str = milestone
        schema: Dict[str, Any] = SCHEMAS[milestone]
        admin_token: Optional[str] = authenticate()
        if not admin_token:
            raise Exception("Failed to authenticate admin.")
        if not collection_exists(collection_name, admin_token):
            create_or_update_pocketbase_collection(
                collection_name=collection_name,
                schema=schema,
                admin_token=admin_token,
                collection_type='base',
                listRule=None,
                viewRule=None,
                options={}
            )
def collection_exists(collection_name: str, admin_token: str) -> bool:
    """
    Helper function to check if a collection already exists in PocketBase.
    """
    import requests
    pocketbase_url = os.getenv('POCKETBASE_URL')
    url = f"{pocketbase_url}/api/collections/{collection_name}"

    response = requests.get(url, headers={
        "Authorization": admin_token
    })

    return response.status_code == 200  # Collection exists if status is 200
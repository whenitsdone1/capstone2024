import requests
from typing import Dict, List, Any, Optional
from utility_services import get_url, authenticate
from db_schema import SCHEMAS
from datetime import datetime
from flask import current_app

# This was intended to be used for visualisations, but now it just feeds data to the LLM for tailored advice.


def get_user_metrics(email: str) -> Dict[str, Any]: 
    """
    Retrieves user metrics for a given email.

    Args:
        email (str): The email of the user to get metrics for.

    Returns:
        Dict[str, Any]: A dictionary containing the user's email and submission metrics.
    """
    url: str = f"{get_url()}/api/collections"
    headers: Dict[str, str] = {
        "Content-Type": "application/json",
        "Authorization": authenticate()
    }

    user_metrics: Dict[str, Any] = {
        'email': email,
        'submissions': []
    }

    for milestone in SCHEMAS.keys(): 
        collection_name: str = f"{milestone}"
        response: requests.Response = requests.get(f"{url}/{collection_name}/records", headers=headers)

        if response.status_code == 200:
            data: Dict[str, Any] = response.json()
            submissions: List[Dict[str, Any]] = data.get('items', [])

            # Filter submissions by matching email
            for submission in submissions:
                if submission.get('email') != email:
                    continue  # Skip if the email doesn't match

                start_time: Optional[str] = submission.get('start_time')
                completion_time: Optional[str] = submission.get('completion_time')
                time_taken: Optional[float] = None  # Time taken in minutes

                if start_time and completion_time:
                    start_time_dt: datetime = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    completion_time_dt: datetime = datetime.fromisoformat(completion_time.replace('Z', '+00:00'))
                    time_taken = (completion_time_dt - start_time_dt).total_seconds() / 60

                boolean_fields: Dict[str, bool] = {
                    field: submission[field] for field in submission 
                    if field not in ['id', 'collectionId', 'collectionName', 'created', 'updated']
                    and next((f for f in SCHEMAS[milestone] if f['name'] == field), {}).get('type') == 'bool'
                }

                submission_data: Dict[str, Any] = {
                    'milestone': milestone,
                    'start_time': start_time,
                    'completion_time': completion_time,
                    'time_taken_minutes': time_taken,
                    'boolean_responses': boolean_fields,
                }

                user_metrics['submissions'].append(submission_data)
        else:
            current_app.logger.error(f"Failed to retrieve submissions for {collection_name}. Status code: {response.status_code}")
            current_app.logger.error(f"Response data: {response.text}")

    return user_metrics


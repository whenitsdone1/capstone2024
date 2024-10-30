import requests
from flask import current_app
from datetime import datetime, date
from typing import Optional, Dict
import re


def determine_form(term_start_date: Optional[date] = None, semesters=False) -> Optional[str]:
    """Determine which form is being submitted using the date - Milestone 1 is due before the end of week one (7 days after term start),
       Milestone 2 is due before the end of week 3 (21 days after term start),
       Milestone 3 is due before the end of week 6 (42 days after term start),
       Any submissions greater than 42 days are assumed to be the Milestone 1 submission for the coming term.
       For semesters (when semesters=True) the dates are slightly different, but the principle is the same."""
    if not term_start_date:
        current_app.logger.error("Term start date not provided.")
        return None
    current_date = get_AEST_date()  # Get current date
    if not current_date:
        current_app.logger.error("Failed to get the current date.")
        return None
    if isinstance(term_start_date, datetime):
        term_start_date = term_start_date.date()
        # Clean the term_start_date string if it contains extra time information
    try:
        # Use regex to remove time components if present (e.g., "00:00:00.000Z")
        clean_date_str = re.sub(r"T.*", "", term_start_date) if 'T' in str(term_start_date) else str(term_start_date)
        clean_date_str = str(clean_date_str).split(' ')[0]  # Remove any trailing space-time portion
        # Parse the cleaned date string
        term_start_date= datetime.strptime(clean_date_str, "%Y-%m-%d").date()
    except ValueError as e:
        current_app.logger.error(f"Invalid term start date format: {e}")
        return None
    days_since_period_start = abs((current_date - term_start_date).days)
    MILESTONES: Dict[str, Dict[str, int]] = {
        "weeks_2_3": {"start": 7, "end": 14},  # Milestone 2 day ranges
        "weeks_4_6": {"start": 15, "end": 42},  # Milestone 3 day ranges
    }
    SEM_MILESTONES: dict = {"weeks_2_3": {"start": 7, "end": 35}, "weeks_4_6": {"start": 36, "end": 77}}

    # If passed a form from a semester (when semesters = True) use day ranges from SEM_MILESTONES
    if semesters:
        if SEM_MILESTONES["weeks_2_3"]["start"] <= days_since_period_start <= SEM_MILESTONES["weeks_2_3"]["end"]:
            return "Milestone_2"
        elif SEM_MILESTONES["weeks_4_6"]["start"] <= days_since_period_start <= SEM_MILESTONES["weeks_4_6"]["end"]:
            return "Milestone_3"
        else:
            return "Milestone_1"  # Upcoming term

    # Determine the correct form period based on the number of days since the terms start date
    if MILESTONES["weeks_2_3"]["start"] <= days_since_period_start <= MILESTONES["weeks_2_3"]["end"]:
        return "Milestone_2"
    elif MILESTONES["weeks_4_6"]["start"] <= days_since_period_start <= MILESTONES["weeks_4_6"]["end"]:
        return "Milestone_3"
    else:
        return "Milestone_1"  # Upcoming term

# Poll API for AEST date-time object
def get_AEST_date() -> Optional[date]:
    api_url = "https://worldtimeapi.org/api/timezone/Australia/Melbourne"
    try:
        response: requests.Response = requests.get(api_url)
        response.raise_for_status()  # Write bad status codes to logs
        data: Dict[str, str] = response.json()
        date_str: str = data['datetime'].split(
            'T')[0]  # Extract the date from response
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except requests.RequestException as e:
        current_app.logger.error(
            f"An error occurred fetching current date from API: {e}")
        return None

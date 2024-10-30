from flask import Blueprint, jsonify, Response, current_app
import requests
from typing import List, Dict, Union
from utility_services import authenticate, get_url
from db_schema import SCHEMAS

admin_bp = Blueprint('admin', __name__)

# Type Definitions 
RecordSummary = Dict[str, Union[str, None]]
JsonResponse = Union[Response, tuple]


@admin_bp.route('/admin/records', methods=['GET'])
def admin_get_all_records() -> JsonResponse:
    """
    Admin route to get all records from all collections.
    """
    current_app.logger.info("Fetching all records from all collections.")
    url: str = f"{get_url()}/api/collections"
    headers: Dict[str, str] = {
        "Content-Type": "application/json",
        "Authorization": authenticate()
    }
    all_records: List[RecordSummary] = []

    for milestone in SCHEMAS.keys():
        collection_name: str = f"{milestone}"
        current_app.logger.info(
            f"Fetching records from collection: {collection_name}")
        response: requests.Response = requests.get(
            f"{url}/{collection_name}/records", headers=headers)
        if response.status_code == 200:
            data: Dict[str, Union[List[Dict], str]] = response.json()
            records: List[Dict] = data.get('items', [])
            for record in records:
                record_summary: RecordSummary = {
                    'name': record.get('name'),
                    'id': record.get('id'),
                    'email': record.get('email'),
                    'milestone': milestone,
                    'submission_date': record.get('created')
                }
                if record_summary:
                    all_records.append(record_summary)
            current_app.logger.info(
                f"Successfully fetched {len(records)} records from {collection_name}.")
        else:
            current_app.logger.error(
                f"Failed to retrieve records for {collection_name}. Status code: {response.status_code}")
            current_app.logger.error(f"Response data: {response.text}")
            continue

    if all_records:
        current_app.logger.info(
            f"Successfully fetched all records. Total records: {len(all_records)}.")
        return jsonify(all_records), 200
    else:
        current_app.logger.error(
            "Unable to retrieve any records from the database.")
        return jsonify({'error': 'No records found'}), 500


@admin_bp.route('/admin/records/<record_id>', methods=['GET'])
def admin_get_record(record_id: str) -> JsonResponse:
    """
    Admin route to get detailed data for a specific record, which can be used for visualizations.
    """
    current_app.logger.info(f"Fetching record with ID: {record_id}.")
    url: str = f"{get_url()}/api/collections"
    headers: Dict[str, str] = {
        "Content-Type": "application/json",
        "Authorization": authenticate()
    }

    for milestone in SCHEMAS.keys():
        collection_name: str = f"{milestone}"
        response: requests.Response = requests.get(
            f"{url}/{collection_name}/records/{record_id}", headers=headers)
        if response.status_code == 200:
            current_app.logger.info(
                f"Successfully fetched record {record_id} from {collection_name}.")
            record: Dict = response.json()
            return jsonify(record), 200
        else:
            current_app.logger.warning(
                f"Failed to find record {record_id} in {collection_name}.")
            continue

    current_app.logger.error(
        f"Record with ID {record_id} not found in any collection.")
    return jsonify({'error': 'Record not found'}), 404

from flask import jsonify, request, current_app, Response
from datetime import datetime
from typing import Optional, Dict
from utility_services import authenticate, get_url
from date import determine_form
from db_schema import SCHEMAS
from db_util import create_or_update_pocketbase_collection
import requests
import requests
from pocketbase import PocketBase

pb = PocketBase(get_url())
Json = Dict[str, any]

def form_submit() -> Response:
    pb.auth_store.save(authenticate())
    form_data = request.json
    try:
        term_start_date: datetime = datetime.strptime(form_data.get("term_start_date"), "%Y-%m-%d")
    except Exception as e:
        current_app.logger.error("Error retrieving start_data from form")
        return jsonify({"error": "Invalid date format"}), 400 
    milestone: Optional[str] = determine_form(term_start_date)
    if not milestone:
        current_app.logger.error("Could not find active milestone for the current date")
        return jsonify({"message": "No active milestone for the current date"}), 400
    collection_name: str = f"{milestone}"
    admin_token: Optional[str] = authenticate()
    if not admin_token:
        current_app.logger.error("Error authenticating with PB")
        return jsonify({"error": "Failed to authenticate with PocketBase"}), 500
    create_or_update_pocketbase_collection(
        collection_name=collection_name,
        schema=SCHEMAS[milestone],
        admin_token=admin_token,
        collection_type='base',
        listRule=None,
        viewRule=None,
        options={}
    )
    headers = {
            "Authorization": f"{authenticate()}"
        }
    response = requests.get(f'{get_url()}/api/collections/{collection_name}', headers=headers)
    collection_schema = response.json()
    record_data = {field['name']: form_data.get(field['name']) for field in collection_schema['schema']}
    headers: Dict[str, str] = {
        "Content-Type": "application/json",
        "Authorization": admin_token
    }
    url: str = f"{get_url()}/api/collections/{collection_name}/records"
    response: requests.Response = requests.post(url, json=record_data, headers=headers)
    if response.status_code in [200, 201]:
        record_id = response.json().get("id")
        return jsonify({"message": "Form submission successful", "record_id": record_id}), 200
    else:
        current_app.logger.error(f"Failed to submit form, error: {response.text}")
        current_app.logger.error("Raw data from failed request:\n", form_data)
        return jsonify({"message": "Failed to submit form", "error": response.text}), 400

def delete_logic(id: str, term_start_date) -> Response:
    try:
        collection_name: str = f"{determine_form(term_start_date)}"
        admin_token: Optional[str] = authenticate()
        if not admin_token:
            current_app.logger.error("Failed to authenticate with PocketBase.")
            return jsonify({"error": "Failed to authenticate with PocketBase"}), 500

        headers: Dict[str, str] = {"Authorization": admin_token}
        response: requests.Response = requests.delete(
            f"{get_url()}/api/collections/{collection_name}/records/{id}",
            headers=headers,
        )
        if response.status_code == 204:
            current_app.logger.info(f"Record deleted successfully: record_id={id}")
            return "", 204
        elif response.status_code == 404:
            current_app.logger.error(f"Attempted deletion of non-existent record, record_id={id}")
            return jsonify({"error": "Record not found"}), 404
        else:
            current_app.logger.error(
                f"Failed to delete record. Status code: {response.status_code}, Response: {response.text}"
            )
            return jsonify({"error": "Failed to delete record", "details": response.text}), response.status_code
    except Exception as e:
        current_app.logger.exception(f"An unexpected error occurred while deleting the record: {e}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

def get_logic(id: str, term_start_date) -> Response:
    try:
        collection_name: str = f"{determine_form(term_start_date)}"  
        admin_token: Optional[str] = authenticate()
        if not admin_token:
            current_app.logger.error("Failed to authenticate with PocketBase.")
            return jsonify({"error": "Failed to authenticate with PocketBase"}), 500
        headers: Dict[str, str] = {"Authorization": admin_token}
        response: requests.Response = requests.get(
            f"{get_url()}/api/collections/{collection_name}/records/{id}",
            headers=headers,
        )
        if response.status_code == 200:
            current_app.logger.info(f"Record retrieved successfully: {response.json()}")
            return jsonify({"reponse data": response.json(), "record_id": id}), 200
        elif response.status_code == 404:
            current_app.logger.error(f"Record not found: record_id={id}")
            return jsonify({"error": "Record not found"}), 404
        else:
            current_app.logger.error(
                f"Failed to retrieve record. Status code: {response.status_code}, Response: {response.text}"
            )
            return jsonify({"error": "Failed to retrieve record", "details": response.text}), response.status_code
    except Exception as e:
        current_app.logger.exception(f"An unexpected error occurred while retrieving the record: {e}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500
def update_logic(id, term_start_date) -> Response:
    try:
        data = request.json
        if not data:
            current_app.logger.error("No JSON data provided in the request.")
            return jsonify({"error": "No JSON data provided"}), 400
        collection_name: str = f"{determine_form(term_start_date)}"
        admin_token: Optional[str] = authenticate()
        if not admin_token:
            current_app.logger.error("Failed to authenticate with PocketBase.")
            return jsonify({"error": "Failed to authenticate with PocketBase"}), 500
        headers: Dict[str, str] = {"Authorization": admin_token, "Content-Type": "application/json"}
        response: requests.Response = requests.patch(
            f"{get_url()}/api/collections/{collection_name}/records/{id}",
            json=data,
            headers=headers,
        )
        if response.status_code == 200:
            current_app.logger.info(f"Record updated successfully: {response.json()}")
            return jsonify(response.json()), 200
        elif response.status_code == 404:
            current_app.logger.error(f"Record not found for updating: record_id={id}")
            return jsonify({"error": "Record not found"}), 404
        else:
            current_app.logger.error(
                f"Failed to update record. Status code: {response.status_code}, Response: {response.text}"
            )
            return jsonify({"error": "Failed to update record", "details": response.text}), response.status_code
    except Exception as e:
        current_app.logger.exception(f"An unexpected error occurred while updating the record: {e}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

import requests
from typing import Dict, Any, Optional
from flask import current_app, jsonify, request, send_file, Response
import pandas as pd
from utility_services import get_url
from date import determine_form
from utility_services import authenticate
from io import BytesIO

def parse_spreadsheet(sem=False) -> Response:
    """
    Parses an uploaded spreadsheet, extracts data, and creates a record in the appropriate PocketBase collection.

    Returns:
        Response: Flask JSON response indicating success or failure.
    """
    try:
        if 'file' not in request.files:
            current_app.logger.error("No file part in the request.")
            return jsonify({"error": "No file part in the request"}), 400
        file = request.files['file']
        if file.filename == '':
            current_app.logger.error("No selected file.")
            return jsonify({"error": "No selected file"}), 400
        allowed_extensions = {'xls', 'xlsx'}
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            current_app.logger.error("Invalid file extension.")
            return jsonify({"error": "Invalid file extension"}), 400
        df: pd.DataFrame = pd.read_excel(file)
        if 'Field' in df.columns and 'Value' in df.columns:
            form_data = pd.Series(df['Value'].values, index=df['Field']).to_dict()
        else:
            form_data: Dict[str, Any] = df.iloc[0].to_dict()
        term_start_date_str: Optional[str] = form_data.get("term_start_date")
        academic_period: Optional[str] = form_data.get("academic_period", None)
        if sem:
            form_data["academic_period"] = "Semester"
        if not sem and academic_period == None:
            form_data["academic_period"] = "Term"
        if academic_period == "Semester":
              milestone: Optional[str] = determine_form(term_start_date_str, semesters=True)
        else:
            milestone: Optional[str] = determine_form(term_start_date_str)
        if not milestone:
            return jsonify({"message": "No active milestone for the current date"}), 400
        collection_name: str = f"{milestone}"
        record_data: Dict[str, Any] = form_data.copy()
        url: str = f"{get_url()}/api/collections/{collection_name}/records"
        headers: Dict[str, str] = {"Content-Type": "application/json"}
        headers['Authorization'] = f'{authenticate()}'

        response: requests.Response = requests.post(
            url, json=record_data, headers=headers)
        record_id = response.json().get("id")
        if response.status_code in [200, 201]:
            current_app.logger.info(
                f"Record created successfully from spreadsheet: {response.json()}")
            return jsonify({"message": "Spreadsheet parsed and record created successfully", "record_id": record_id}), 200
        else:
            current_app.logger.error(
                f"Failed to create record from spreadsheet. Status code: {response.status_code}, Response: {response.text}"
            )
            return (
                jsonify(
                    {"error": "Failed to create record from spreadsheet", "details": response.text}),
                response.status_code,
            )
    except Exception as e:
        current_app.logger.exception(
            f"An unexpected error occurred while parsing the spreadsheet: {e}")
        return (
            jsonify({"error": "An unexpected error occurred", "details": str(e)}),
            500,
        )


def export_spreadsheet(record_id, term_start_date=None, collection_name=None) -> Response:
    """
    Exports a record from PocketBase as a downloadable spreadsheet.

    Args:
        milestone (str): The milestone name for the collection.
        record_id (str): The ID of the record to export.

    Returns:
        Response: Flask response to download the spreadsheet or an error message.
    """
    admin_token = authenticate()

    if not admin_token:
        current_app.logger.error("Failed to authenticate with PocketBase.")
        return jsonify({"error": "Failed to authenticate with PocketBase"}), 500

    def inner(collection_name): # Helper function fetches the record by term_start_date or by passed collection_name.
        if term_start_date is None:
            headers: Dict[str, str] = {"Authorization": f"{admin_token}"}
            response: requests.Response = requests.get(
                f"{get_url()}/api/collections/{collection_name}/records/{record_id}",
                headers=headers,
            )
            if response.status_code == 200:
                return response.json()

        collection_name: str = determine_form(term_start_date)
        headers: Dict[str, str] = {"Authorization": f"{admin_token}"}
        response: requests.Response = requests.get(
            f"{get_url()}/api/collections/{collection_name}/records/{record_id}",
            headers=headers,
        )
        if response.status_code == 200:
            return response.json()

    try:
        record: Dict[str, Any] = inner(collection_name)
        data = [(k, v if v else "No response provided") for k, v in record.items()]  # Impute empty fields
        df: pd.DataFrame = pd.DataFrame(data, columns=["Field", "Value"])
        df = df.sort_values(by="Field")

        # Prepare the output stream for Excel
        output: BytesIO = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            workbook = writer.book
            worksheet = workbook.add_worksheet(f"Record{record_id}")

            # Define formatting
            header_format = workbook.add_format({
                'bold': True, 'font_size': 16, 'align': 'center', 'valign': 'vcenter'
            })
            cell_format = workbook.add_format({
                'font_size': 14, 'align': 'left', 'valign': 'top'
            })
            wrap_format = workbook.add_format({
                'font_size': 14, 'align': 'left', 'valign': 'top', 'text_wrap': True
            })

            # Set column width and text wrapping
            worksheet.set_column('A:A', 25, cell_format)  # Field column width
            worksheet.set_column('B:B', 50, wrap_format)  # Value column width with wrapping

            # Freeze the header row
            worksheet.freeze_panes(1, 0)

            # Write headers
            worksheet.write('A1', 'Field', header_format)
            worksheet.write('B1', 'Value', header_format)

            # Write the data to the sheet
            for i, (field, value) in enumerate(data, start=1):
                worksheet.write(i, 0, field, cell_format)
                worksheet.write(i, 1, str(value), wrap_format)

        output.seek(0)
        current_app.logger.info(f"Exported record {record_id} to spreadsheet.")
        return send_file(
            output,
            download_name=f"record_{record_id}.xlsx",
            as_attachment=True,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        current_app.logger.exception(
            f"An unexpected error occurred while exporting the spreadsheet: {e}"
        )
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

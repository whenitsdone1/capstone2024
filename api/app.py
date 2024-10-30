from flask import Flask, jsonify, request
from flask_cors import CORS
from core_api_logic import *
from utility_services import *
from metrics import get_user_metrics
from admin import admin_bp
from spreadsheets import *
from handle_PB import *
import signal
from datetime import datetime
from adminview import admin_frontend
from home import home


def startup():
    app = Flask(__name__)
    CORS(app)
    setup_logging(app)
    app.register_blueprint(home) 
    app.register_blueprint(admin_bp)
    app.register_blueprint(admin_frontend)
    # Check if PocketBase is running, if not, start it
    ensure_pocketbase_running(app)
    with app.app_context():
        initialize_collections()  # Initialize DB collections in PocketBase
        # End pocketbase if the application is closed
    signal.signal(signal.SIGINT, lambda s, f: handle_exit_signals(s, f, app))
    signal.signal(signal.SIGTERM, lambda s, f: handle_exit_signals(s, f, app))
    return app


app = startup()



@app.route('/api/submit_form', methods=['POST'])
def submit_form():  # Post new entries to database
    return form_submit()


@app.errorhandler(404)  # Handle and write 404s to logs.
def page_not_found(error):
    app.logger.error(
        f"Attempted access to invalid URL: {request.url}: error: {error}")
    return jsonify({"Error": "Requested resource was not found on the server"}), 404


@app.route("/api/delete_record/<record_id>", methods=["DELETE"])
def delete_record(record_id):
    term_start_date_str = request.args.get('term_start_date')
    if not term_start_date_str:
        return app.logger.error({"error": "Term start date not provided"}), 400
    try:
        # Parse the period from the request parameters
        term_start_date = datetime.fromisoformat(term_start_date_str).date()
    except ValueError:
        return app.logger.error({"error": "Invalid term start date format"}), 400
    return delete_logic(record_id, term_start_date)


@app.route("/api/get_record/<record_id>", methods=["GET"])
def get_record(record_id):
    term_start_date_str = request.args.get('term_start_date')
    if not term_start_date_str:
         return get_logic(record_id)
    try:
        term_start_date = datetime.fromisoformat(term_start_date_str).date()
    except ValueError:
        return app.logger.error({"error": "Invalid term start date format"}), 400
    return get_logic(record_id, term_start_date)


@app.route("/api/update_record/<record_id>", methods=["PATCH"])
def update_record(record_id):
    term_start_date_str = request.args.get('term_start_date')
    if not term_start_date_str:
        return app.logger.error({"error": "Need to provide term start date."}), 400
    try:
        term_start_date = datetime.fromisoformat(term_start_date_str).date()
    except ValueError:
        return app.logger.error({"error": "Invalid term start date format"}), 400
    return update_logic(record_id, term_start_date)


@app.route("/api/add_spreadsheet", methods=["POST"])
def add_spreadsheet():
    sem = request.args.get('academicPeriod', "Term") 
    return parse_spreadsheet(sem=True) if sem == "Semester" else parse_spreadsheet()


@app.route("/api/get_spreadsheet/<record_id>", methods=["GET"])
def get_spreadsheet(record_id):
    term_start_date = request.args.get('term_start_date')
    collection_name = request.args.get('milestone')
    if not term_start_date and not collection_name:
        return app.logger.error({"error": "Need to provide either collection name or term start date in request parameters."}), 400
    try:
        if term_start_date:
            term_start_date = datetime.fromisoformat(term_start_date).date()
    except ValueError:
        return app.logger.error({"error": "Invalid term start date format"}), 400
    return export_spreadsheet(record_id, term_start_date, collection_name)


@app.route('/api/metrics/<record_id>', methods=['GET'])
def user_metrics(record_id): # More accurately get user data
    return jsonify(get_user_metrics(record_id))


if __name__ == "__main__":
    app.run(debug=True, port=5000) # Turn debug to false in prod, and add app.config['ENV'] = 'production'


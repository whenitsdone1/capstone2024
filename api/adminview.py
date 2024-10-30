from flask import render_template_string, Blueprint, jsonify, current_app
import requests
from utility_services import authenticate
from typing import List, Dict
from datetime import datetime
import os
from zoneinfo import ZoneInfo

admin_frontend = Blueprint('admin_frontend', __name__)



def format_date_aest(value):
    if not value:
        return "No date provided"
    try:
        if isinstance(value, str):
            utc_dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        else:
            utc_dt = value
        aest_dt = utc_dt.astimezone(ZoneInfo("Australia/Sydney"))
        return aest_dt.strftime("%d %b %Y, %I:%M %p AEST")
    except Exception as e:
        print(f"Error converting date: {e}")
        return str(value)

@admin_frontend.app_template_filter('format_date') # Dates in PB are by default in UTC - apply a filter to convert timezone display to AEST
def format_date_filter(value):
    return format_date_aest(value)

# Render JS, HTML, and CSS to display admin panel
HTML_TEMPLATE = """
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .header {
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .collection-section {
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        th {
            background: #f8f9fa;
            font-weight: 600;
        }
        tr:hover {
            background: #f8f9fa;
            cursor: pointer;
        }
        .stats {
            display: inline-block;
            background: #e9ecef;
            padding: 4px 8px;
            border-radius: 4px;
            margin-right: 10px;
            font-size: 0.9em;
        }
        .empty-message {
            color: #666;
            font-style: italic;
            padding: 20px;
            text-align: center;
        }
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            z-index: 1000;
            overflow-y: auto; 
        }
        .modal-content {
            position: relative;
            background-color: #fff;
            margin: 20px auto;
            padding: 20px;
            width: 95%; 
            max-width: 1100px; 
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            max-height: 85vh; 
            overflow-y: auto;
            font-size: 0.9rem; 
        }
        .detail-row {
            display: flex;
            align-items: center;
            justify-content: space-between; 
            border-bottom: 1px solid #eee;
            padding: 10px 0;
        }
        .detail-label {
            flex: 0 0 40%; 
            font-weight: 600;
            color: #555;
            word-break: break-word; 
            padding-right: 10px;
            text-align: left;
        }
        .detail-value {
            flex: 1;
            word-break: break-word;
            padding-left: 10px;
            text-align: left; 
        }
        .close-button {
            position: absolute;
            right: 20px;
            top: 20px;
            font-size: 24px;
            cursor: pointer;
            color: #666;
            background: #fff;
            padding: 10px;
            z-index: 1;
        }
        .close-button:hover {
            color: #333;
        }
        .no-data {
            color: #666;
            font-style: italic;
        }
        .loading {
            text-align: center;
            padding: 20px;
            font-style: italic;
            color: #666;
        }
        .download-btn {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 0.85em;
            color: #495057;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .download-btn:hover {
            background: #e9ecef;
            border-color: #ced4da;
        }
        .download-btn:active {
            background: #dee2e6;
        }
        .action-cell {
            white-space: nowrap;
            width: 1%;
        }
        @media (max-width: 768px) {
            .detail-row {
                flex-wrap: wrap; 
            }
            .detail-label {
                flex: 0 0 100%; 
                margin-bottom: 5px;
            }
            .detail-value {
                flex: 0 0 100%; 
                padding-left: 0;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Admin Dashboard</h1>
        <div>
            <span class="stats">Total Collections: {{ total_collections }}</span>
            <span class="stats">Total Records: {{ total_records }}</span>
        </div>
    </div>
    
    {% for milestone, records in records_by_milestone.items() %}
    <div class="collection-section">
        <h2>{{ milestone }}</h2>
        {% if records %}
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>ID</th>
                    <th>Email</th>
                    <th>Submission Date</th>
                    <th></th>
                </tr>
            </thead>
            <tbody>
                {% for record in records %}
                <tr>
                    <td onclick="showDetails('{{ record.id }}', '{{ record.milestone }}')">
                        {% if record.name %}
                            {{ record.name }}
                        {% else %}
                            <span class="no-data">No name provided</span>
                        {% endif %}
                    </td>
                    <td onclick="showDetails('{{ record.id }}', '{{ record.milestone }}')">{{ record.id }}</td>
                    <td onclick="showDetails('{{ record.id }}', '{{ record.milestone }}')">
                        {% if record.email and record.email.strip() %}
                            {{ record.email }}
                        {% else %}
                            <span class="no-data">No email provided</span>
                        {% endif %}
                    </td>
                    <td onclick="showDetails('{{ record.id }}', '{{ record.milestone }}')">{{ record.submission_date | format_date }}</td>
                    <td class="action-cell">
                        <button 
                            class="download-btn"
                            onclick="downloadSpreadsheet('{{ record.id }}', '{{ milestone }}')"
                            title="Download as spreadsheet"
                        >
                            ↓ Download
                        </button>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p class="empty-message">No records found in this collection.</p>
        {% endif %}
    </div>
    {% endfor %}

    <div id="recordModal" class="modal">
        <div class="modal-content">
            <span class="close-button" onclick="closeModal()">&times;</span>
            <h2>Record Details</h2>
            <div id="recordDetails">
                <p class="loading">Loading details...</p>
            </div>
        </div>
    </div>

    <script>
        function showDetails(recordId, milestone) {
            const modal = document.getElementById('recordModal');
            const detailsDiv = document.getElementById('recordDetails');
            modal.style.display = 'block';
            detailsDiv.innerHTML = '<p class="loading">Loading details...</p>';
            
            fetch(`/admin/record-details/${milestone}/${recordId}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.error) {
                        detailsDiv.innerHTML = `<p class="error">${data.error}</p>`;
                        return;
                    }

                    const recordData = data.items?.[0] || data;
                    let detailsHTML = '';
                    const expandedData = data.expand || {};
                    
                    for (const [key, value] of Object.entries(recordData)) {
                        if (key !== 'id' && key !== 'milestone') {
                            let displayValue = value;
                            
                            if (expandedData[key]) {
                                displayValue = expandedData[key].name || expandedData[key].title || JSON.stringify(expandedData[key]);
                            }
                            
                            if (displayValue === null || displayValue === undefined || displayValue === '') {
                                displayValue = '<span class="no-data">Not provided</span>';
                            }
                            
                            detailsHTML += `
                                <div class="detail-row">
                                    <div class="detail-label">${key.replace(/_/g, ' ').charAt(0).toUpperCase() + key.slice(1)}</div>
                                    <div class="detail-value">${displayValue}</div>
                                </div>
                            `;
                        }
                    }
                    
                    if (Object.keys(expandedData).length > 0) {
                        detailsHTML += `
                            <div class="detail-row">
                                <div class="detail-label">Related Data</div>
                                <div class="detail-value">
                                    <pre>${JSON.stringify(expandedData, null, 2)}</pre>
                                </div>
                            </div>
                        `;
                    }
                    
                    detailsDiv.innerHTML = detailsHTML;
                })
                .catch(error => {
                    detailsDiv.innerHTML = `<p class="error">Error loading record details: ${error.message}</p>`;
                    console.error('Error:', error);
                });
        }

        function closeModal() {
            const modal = document.getElementById('recordModal');
            modal.style.display = 'none';
        }

        window.onclick = function(event) {
            const modal = document.getElementById('recordModal');
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        }

        function downloadSpreadsheet(recordId, milestone) {
            event.stopPropagation();
            const url = `/api/get_spreadsheet/${recordId}?milestone=${encodeURIComponent(milestone)}`;
            const link = document.createElement('a');
            link.href = url;
            link.download = `${milestone}_record_${recordId}.xlsx`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    </script>
</body>
</html>
"""

def format_date(date_str: str) -> str:
    """Format the date string for display"""
    try:
        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return date_obj.strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, AttributeError):
        return date_str

# Register the template filter
@admin_frontend.app_template_filter('format_date')
def format_date_filter(date_str):
    return format_date(date_str)

@admin_frontend.route('/admin/dashboard')
def admin_dashboard():
    """Render the admin dashboard with all records"""
    try:
        # Make request to the API endpoint we already have
        response = requests.get('http://localhost:5000/admin/records')
        if response.status_code != 200:
            return f"Error fetching records: {response.status_code}", 500
        records = response.json()
        # Organize records by milestone
        records_by_milestone: Dict[str, List[Dict]] = {}
        for record in records:
            milestone = record['milestone']
            if milestone not in records_by_milestone:
                records_by_milestone[milestone] = []
            records_by_milestone[milestone].append(record)
        # Calculate statistics
        total_collections = len(records_by_milestone)
        total_records = len(records)
        return render_template_string(
            HTML_TEMPLATE,
            records_by_milestone=records_by_milestone,
            total_collections=total_collections,
            total_records=total_records
        )
    
    except Exception as e:
        return f"Error: {str(e)}", 500

@admin_frontend.route('/admin/record-details/<milestone>/<record_id>')
def get_record_details(milestone: str, record_id: str):
    """Get detailed information for a specific record from PocketBase"""
    try:
        # Get authentication token
        auth_token = authenticate()
        if not auth_token:
            return jsonify({'error': 'Failed to authenticate with PocketBase'}), 500

        # Construct the PocketBase request
        url = f"{os.getenv('POCKETBASE_URL')}/api/collections/{milestone}/records/{record_id}"
        
        # Make request to PocketBase with authentication
        response = requests.get(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": auth_token
            }
        )
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            error_data = response.json() if response.content else {'error': 'Failed to fetch record details'}
            return jsonify(error_data), response.status_code
            
    except Exception as e:
        current_app.logger.exception("Error fetching record details")
        return jsonify({'error': str(e)}), 500
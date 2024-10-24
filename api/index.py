from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

def download_file(url, file_name):
    """Download a file from the given URL."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an error for bad responses
        with open(file_name, 'wb') as f:
            f.write(response.content)
        return file_name
    except requests.RequestException as e:
        print(f"Error downloading file: {e}")  # Log the error for debugging
        return None

def upload_to_gofile(file_path):
    """Upload the downloaded file to Gofile.io."""
    upload_url = "https://store1.gofile.io/uploadFile"
    try:
        with open(file_path, 'rb') as file_data:
            response = requests.post(upload_url, files={'file': file_data})
        response.raise_for_status()  # Raise an error for bad responses

        response_json = response.json()
        if response_json.get("status") == "ok":
            return response_json["data"]["downloadPage"]
    except requests.RequestException as e:
        print(f"Error uploading to Gofile: {e}")  # Log the error for debugging
    return None

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """API endpoint to handle file upload."""
    try:
        data = request.json
        url = data.get('url')
        if not url:
            return jsonify({"error": "URL is required"}), 400

        file_name = url.split("/")[-1]
        file_path = download_file(url, file_name)

        if file_path:
            gofile_link = upload_to_gofile(file_path)
            if gofile_link:
                os.remove(file_path)  # Clean up the file after upload
                return jsonify({"gofile_link": gofile_link}), 200
            return jsonify({"error": "Failed to upload to Gofile"}), 500

        return jsonify({"error": "Failed to download file"}), 500

    except Exception as e:
        print(f"Unexpected error: {e}")  # Log unexpected errors
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

# No app.run() needed for Vercel deployment


from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

def upload_to_gofile(file_stream, file_name):
    """Upload the file stream to Gofile.io."""
    upload_url = "https://store1.gofile.io/uploadFile"
    try:
        response = requests.post(upload_url, files={file_name: file_stream})
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

        # Stream the file directly to Gofile
        with requests.get(url, stream=True) as response:
            response.raise_for_status()  # Raise an error for bad responses
            gofile_link = upload_to_gofile(response.raw, url.split("/")[-1])

            if gofile_link:
                return jsonify({"gofile_link": gofile_link}), 200
            return jsonify({"error": "Failed to upload to Gofile"}), 500

    except Exception as e:
        print(f"Unexpected error: {e}")  # Log unexpected errors
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

# No app.run() needed for Vercel deployment


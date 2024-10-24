from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Your existing code here...
def download_file(url, file_name):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(file_name, 'wb') as f:
            f.write(response.content)
        return file_name
    return None

def upload_to_gofile(file_path):
    upload_url = "https://store1.gofile.io/uploadFile"
    with open(file_path, 'rb') as file_data:
        response = requests.post(upload_url, files={'file': file_data})

    if response.status_code == 200:
        response_json = response.json()
        if response_json["status"] == "ok":
            download_link = response_json["data"]["downloadPage"]
            return download_link
    return None

@app.route('/upload', methods=['POST'])
def upload_file():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400

    file_name = url.split("/")[-1]
    file_path = download_file(url, file_name)

    if file_path:
        gofile_link = upload_to_gofile(file_path)
        if gofile_link:
            return jsonify({"gofile_link": gofile_link}), 200
        return jsonify({"error": "Failed to upload to Gofile"}), 500
    return jsonify({"error": "Failed to download file"}), 500

if __name__ == '__main__':
    app.run()

#Rosario Moscato: giugno 2025
import os
import json
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
from datetime import datetime

# --- Configuration ---
# Flowise Configuration
FLOWISE_API_URL = os.environ.get("FLOWISE_API_URL", "http://192.168.1.122:8009/api/v1/prediction/e336ac20-fc71-4d17-baeb-1db07480de2d")
FLOWISE_BEARER_TOKEN = os.environ.get("FLOWISE_BEARER_TOKEN", "iZizq9uRxPLzc9rHfL-bXevYxPfoMiLwf5tcu8SKShw")

# Gemini Configuration (Placeholders)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_PLACEHOLDER")
GEMINI_API_ENDPOINT = os.environ.get("GEMINI_API_ENDPOINT", "YOUR_GEMINI_API_ENDPOINT_PLACEHOLDER") # Not used in placeholder

# Database
# Import database utility functions from database.py
from database import init_db, add_concept_to_archive, get_all_archived_concepts

# --- Flask App Initialization ---
# Serve static files from the root directory where index.html, archive.html, help.html are
app = Flask(__name__, static_folder='..', static_url_path='') 
CORS(app) # Enable CORS for all routes

# --- Flowise Integration ---
def query_flowise(prompt_text):
    # print(f"DEBUG: FLOWISE_API_URL from Python env: {os.environ.get('FLOWISE_API_URL')}") # Kept for debugging if needed
    # print(f"DEBUG: FLOWISE_BEARER_TOKEN from Python env (first 5 chars): {os.environ.get('FLOWISE_BEARER_TOKEN', '')[:5]}")
        
    headers = {"Authorization": f"Bearer {FLOWISE_BEARER_TOKEN}"}
    payload = {"question": prompt_text}
    try:
        response = requests.post(FLOWISE_API_URL, headers=headers, json=payload, timeout=90) # Timeout at 90 seconds
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.Timeout:
        print(f"Timeout error querying Flowise for: {prompt_text} (after 90 seconds)")
        return {"error": "Flowise request timed out (90s)"}
    except requests.exceptions.RequestException as e:
        print(f"Error querying Flowise: {e}")
        return {"error": str(e)}

# --- Gemini Integration (Placeholder) ---
def generate_images_with_gemini(text_input):
    # This is a placeholder. Replace with actual Gemini API call.
    # Instructions for Gemini API Integration are in the README.md and previous comments.
    print(f"Simulating Gemini image generation for: {text_input[:50]}...")
    import time
    time.sleep(1) 
    return {
        "image_urls": [
            "https://lh3.googleusercontent.com/aida-public/AB6AXuDYJBTu_BGsgCpsu_S-0LJDTQeFsPkCPqtNd0UAXUgXqj30-h714TT5qdAhUZ9oq9zLOo_ASXrQbgLIrA6ukmMFx3TEySKr9Jm5pg6-hJ9hOMc29cy5iloBPGNKi2FH4xex8fKqqYS1T4Un2i6qGonVcfWPYFpGZBgfE83sBAmEBlbU-_WiW4xh7Ht06T43PPvvaYIGTrFRycZXPilQBh6WiJssiN6bXZwLWWxqKUmybuINHrX8uqmvPy0N_7WiZoBTITvDt7fyhnY5",
            "https://lh3.googleusercontent.com/aida-public/AB6AXuA8jQT1Rg1U9LLAdL3jlt_zwHjNSjj7QaB8a1WHDbwKz4DwI48q4bAwgtuODTCfXSMSQ-pJQGtbS1HZyWmtuiRHptVRF-1OSWSv6rcnpeGHXmD7oOiqoF37HihRb0V9NcXIL6UlxxjYnIbXc-GyIOlnwEaMGz17xdLIAfidHYud5AAgmBznSkgiFfBaNBVOTxIBbym99ogOkCZ_pkerrvHfXSu8MEvu98bIZcHYx10qU46XR8hpmxzgVNS9X_GGC0QulwOVK8AOE8ud"
        ],
        "error": None 
    }

# --- API Endpoints ---
@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

@app.route('/archive.html') 
def serve_archive_page():
    return app.send_static_file('archive.html')

@app.route('/help.html') 
def serve_help_page():
    return app.send_static_file('help.html')

@app.route('/api/generate', methods=['POST'])
def generate_concept_api():
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "Prompt is required"}), 400

    user_prompt = data['prompt']
    flowise_data = query_flowise(user_prompt)
    if 'error' in flowise_data or not flowise_data.get('text'): 
        error_detail = flowise_data.get('error', 'Unknown error from Flowise or empty text response.')
        print(f"Flowise error: {error_detail}") 
        return jsonify({"error": "Failed to get valid response from Flowise", "details": error_detail}), 500
    
    flowise_text = flowise_data.get('text') 
    gemini_result = generate_images_with_gemini(flowise_text) 
    if gemini_result.get("error") or not gemini_result.get("image_urls"):
        error_detail = gemini_result.get('error', 'Unknown error from Gemini or no image URLs.')
        print(f"Gemini error: {error_detail}") 
        return jsonify({"error": "Failed to generate images with Gemini", "details": error_detail}), 500

    image_urls = gemini_result["image_urls"]
    return jsonify({
        "prompt": user_prompt,
        "flowise_response": flowise_text,
        "gemini_image_urls": image_urls
    })

@app.route('/api/archive', methods=['POST'])
def add_to_archive_api():
    data = request.get_json()
    if not data or 'prompt' not in data or 'flowise_response' not in data or 'gemini_image_urls' not in data:
        return jsonify({"error": "Missing data for archiving (prompt, flowise_response, gemini_image_urls required)"}), 400

    concept_id = add_concept_to_archive(
        data['prompt'], 
        data['flowise_response'], 
        data['gemini_image_urls']
    )
    if concept_id:
        return jsonify({"message": "Concept archived successfully", "id": concept_id}), 201
    else:
        return jsonify({"error": "Failed to archive concept due to database error"}), 500

@app.route('/api/archive', methods=['GET'])
def get_archived_concepts_api():
    archived_items = get_all_archived_concepts()
    return jsonify(archived_items)

# --- Main Execution ---
if __name__ == '__main__':
    if not os.path.exists(app.static_folder):
        print(f"Warning: Static folder '{app.static_folder}' not found. HTML files might not serve.")
    init_db()
    print(f"Starting Flask server. Access at http://127.0.0.1:5001")
    print(f"Serving static files from: {os.path.abspath(app.static_folder)}")
    print(f"Main page: http://127.0.0.1:5001/index.html")
    print(f"Archive page: http://127.0.0.1:5001/archive.html")
    print(f"Help page: http://127.0.0.1:5001/help.html")
    app.run(host='0.0.0.0', port=5001, debug=True)
    
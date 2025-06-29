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
# Serve static files from the root directory where index.html and archive.html are
app = Flask(__name__, static_folder='..', static_url_path='')
CORS(app) # Enable CORS for all routes

# --- Flowise Integration ---
def query_flowise(prompt_text):
    headers = {"Authorization": f"Bearer {FLOWISE_BEARER_TOKEN}"}
    payload = {"question": prompt_text}
    try:
        #response = requests.post(FLOWISE_API_URL, headers=headers, json=payload, timeout=30) # Added timeout
        response = requests.post(FLOWISE_API_URL, headers=headers, json=payload, timeout=90) # Increased timeout to 90 seconds

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
    #
    # Instructions for Gemini API Integration:
    # 1. Install the Google Generative AI SDK:
    #    pip install google-generativeai
    # 2. Import the library in this file:
    #    import google.generativeai as genai
    # 3. Configure the API key (ideally from environment variables):
    #    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    # 4. Choose a suitable Gemini model for image generation.
    #    For example, if there's a model that takes text and returns image URLs or image data.
    #    (Note: As of late 2023, Gemini's direct text-to-image generation API details might vary.
    #     The example below assumes a hypothetical function. Refer to official Gemini documentation.)
    #
    # Example (hypothetical - adapt to actual Gemini SDK):
    # try:
    #     model = genai.GenerativeModel('gemini-pro-vision') # Or a specific image generation model
    #     # The prompt might need to be structured specifically for image generation.
    #     # This might involve telling Gemini to create an image based on the text.
    #     # response = model.generate_content(f"Generate an image based on the following concept: {text_input}")
    #     # image_urls = []
    #     # if response.parts:
    #     #    for part in response.parts:
    #     #        if part.mime_type.startswith("image/"):
    #     #             # If Gemini returns image data, you'd need to save it and return a URL
    #     #             # or if it returns a URL directly.
    #     #             # This part is highly dependent on the Gemini API response structure.
    #     #             # For now, let's assume it might return URLs in a specific way:
    #     #             pass # Replace with actual logic
    #     #
    #     # If the API directly gives URLs (less likely for raw image data models):
    #     # image_urls = [extracted_url1, extracted_url2] # from response object
    #
    #     # For a placeholder, we'll continue to return static URLs.
    #     # When implementing, ensure you handle API errors, rate limits, etc.
    #
    #     print(f"Actual Gemini call would happen here for: {text_input[:50]}...")
    #     # Replace the following with actual image URLs from Gemini
    #     generated_image_urls = [
    #         "https://actual-gemini-image-url-1.jpg",
    #         "https://actual-gemini-image-url-2.jpg"
    #     ]
    #     return {"image_urls": generated_image_urls, "error": None}
    #
    # except Exception as e:
    #     print(f"Error calling Gemini API: {e}")
    #     return {"image_urls": [], "error": str(e)}

    # Current Placeholder Implementation:
    print(f"Simulating Gemini image generation for: {text_input[:50]}...")
    import time
    time.sleep(1) # Reduced delay for faster testing
    # Placeholder image URLs (same as in index.html for now)
    return {
        "image_urls": [
            "https://lh3.googleusercontent.com/aida-public/AB6AXuDYJBTu_BGsgCpsu_S-0LJDTQeFsPkCPqtNd0UAXUgXqj30-h714TT5qdAhUZ9oq9zLOo_ASXrQbgLIrA6ukmMFx3TEySKr9Jm5pg6-hJ9hOMc29cy5iloBPGNKi2FH4xex8fKqqYS1T4Un2i6qGonVcfWPYFpGZBgfE83sBAmEBlbU-_WiW4xh7Ht06T43PPvvaYIGTrFRycZXPilQBh6WiJssiN6bXZwLWWxqKUmybuINHrX8uqmvPy0N_7WiZoBTITvDt7fyhnY5",
            "https://lh3.googleusercontent.com/aida-public/AB6AXuA8jQT1Rg1U9LLAdL3jlt_zwHjNSjj7QaB8a1WHDbwKz4DwI48q4bAwgtuODTCfXSMSQ-pJQGtbS1HZyWmtuiRHptVRF-1OSWSv6rcnpeGHXmD7oOiqoF37HihRb0V9NcXIL6UlxxjYnIbXc-GyIOlnwEaMGz17xdLIAfidHYud5AAgmBznSkgiFfBaNBVOTxIBbym99ogOkCZ_pkerrvHfXSu8MEvu98bIZcHYx10qU46XR8hpmxzgVNS9X_GGC0QulwOVK8AOE8ud"
        ],
        "error": None # Explicitly state no error for successful simulation
    }

# --- API Endpoints ---
@app.route('/')
def serve_index():
    # Serves index.html from the root static folder
    return app.send_static_file('index.html')

@app.route('/archive') # Changed to avoid conflict with /api/archive
def serve_archive_page():
    # Serves archive.html from the root static folder
    return app.send_static_file('archive.html')

@app.route('/api/generate', methods=['POST'])
def generate_concept_api():
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "Prompt is required"}), 400

    user_prompt = data['prompt']

    # 1. Query Flowise
    flowise_data = query_flowise(user_prompt)
    if 'error' in flowise_data or not flowise_data.get('text'):
        error_detail = flowise_data.get('error', 'Unknown error from Flowise or empty text response.')
        print(f"Flowise error: {error_detail}")
        return jsonify({"error": "Failed to get valid response from Flowise", "details": error_detail}), 500

    flowise_text = flowise_data.get('text')

    # 2. Generate Images with Gemini
    gemini_result = generate_images_with_gemini(flowise_text) # Using Flowise text as input
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
    # The get_all_archived_concepts function already handles potential errors and returns a list
    return jsonify(archived_items)

# --- Main Execution ---
if __name__ == '__main__':
    # Ensure the static folder exists (it's the root in this config)
    if not os.path.exists(app.static_folder):
        # This should not happen if running from project root, but good check
        print(f"Warning: Static folder '{app.static_folder}' not found. HTML files might not serve.")

    init_db()  # Initialize the database and create table if it doesn't exist

    # For development, Flask's built-in server is fine.
    # For production, use a WSGI server like Gunicorn.
    # Example: gunicorn -w 4 -b 0.0.0.0:5001 backend.app:app (if running gunicorn from project root)
    print(f"Starting Flask server. Access at http://127.0.0.1:5001")
    print(f"Serving static files from: {os.path.abspath(app.static_folder)}")
    print(f"HTML pages should be at http://127.0.0.1:5001/index.html and http://127.0.0.1:5001/archive.html")
    app.run(host='0.0.0.0', port=5001, debug=True)

    # To run this:
    # 1. Make sure you are in the root directory of the project.
    # 2. Set environment variables for API keys if needed.
    #    export FLOWISE_API_URL="your_flowise_url" (if different from default)
    #    export FLOWISE_BEARER_TOKEN="your_flowise_token" (if different from default)
    #    export GEMINI_API_KEY="your_gemini_key" (placeholder)
    # 3. Run the app: python backend/app.py
    # The backend API will be available at http://127.0.0.1:5001/api/...
    # Frontend HTML files (index.html, archive.html) will be served from the root.
    # Main page: http://127.0.0.1:5001/ or http://127.0.0.1:5001/index.html
    # Archive page: http://127.0.0.1:5001/archive.html (Note: path changed from /archive to /archive.html to avoid conflict)
    # If you had /static in your HTML for JS/CSS, they'd be at http://127.0.0.1:5001/static/...
    # But current plan is to put JS in `static/js` and link as `/static/js/main.js`
    # The Flask static_folder is '..' (project root), so /static/js/main.js will correctly resolve to `../static/js/main.js` relative to app.py,
    # which means project_root/static/js/main.js
    # This needs careful handling of paths in HTML. The plan says `static/js/main.js` which is good.
    # The `static_url_path=''` means that files in `static_folder` are served from root.
    # So, `index.html` is at `/index.html`.
    # If we create `static/js/main.js`, it will be available at `/static/js/main.js`.
    # The current `app = Flask(__name__, static_folder='..', static_url_path='')` means `index.html` is at `/index.html`
    # and `static/js/main.js` (if it exists in root/static/js) would be at `/static/js/main.js`. This seems correct.
    # Let's re-verify: `static_folder='..'` means the parent directory of `backend` (i.e. project root).
    # `static_url_path=''` means that files in `static_folder` are served from the application root.
    # So, `index.html` (in project root) is served at `http://host:port/index.html`.
    # `archive.html` (in project root) is served at `http://host:port/archive.html`.
    # A file `project_root/static/js/main.js` would be served at `http://host:port/static/js/main.js`. This is what we want.
    # The routes `@app.route('/')` and `@app.route('/archive')` need to serve the HTML files correctly.
    # `app.send_static_file('index.html')` will look for `index.html` inside `static_folder` (project root). Correct.
    # `app.send_static_file('archive.html')` will look for `archive.html` inside `static_folder` (project root). Correct.
    # The plan to create `static/js/main.js` and `static/js/archive.js` and link them like `<script src="/static/js/main.js"></script>` is correct.Tool output for `overwrite_file_with_block`:

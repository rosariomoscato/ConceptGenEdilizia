import os
import sqlite3
import datetime # Corrected import
from flask import Flask, jsonify, request, send_from_directory, g

# --- Configuration ---
DEFAULT_FLOWISE_API_ENDPOINT = "http://192.168.1.122:8009/api/v1/prediction/e336ac20-fc71-4d17-baeb-1db07480de2d"
FLOWISE_API_ENDPOINT = os.environ.get("FLOWISE_API_ENDPOINT", DEFAULT_FLOWISE_API_ENDPOINT)

# API Keys - will be loaded from environment variables
FLOWISE_API_KEY = os.environ.get("FLOWISE_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# --- Application Setup ---
app = Flask(__name__, static_folder='static')
app.config['IMAGES_FOLDER'] = os.path.join(os.getcwd(), 'images')
DATABASE_PATH = os.path.join(os.getcwd(), 'archive.db') # Use a constant for clarity

# Ensure images folder exists
if not os.path.exists(app.config['IMAGES_FOLDER']):
    os.makedirs(app.config['IMAGES_FOLDER'])

# --- Database Setup & Interaction ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE_PATH)
        db.row_factory = sqlite3.Row # Access columns by name
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db_schema():
    """Initializes the database schema if the DB file doesn't exist or is empty."""
    db_exists = os.path.exists(DATABASE_PATH)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Check if the table already exists to avoid errors on subsequent runs
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='requests'")
    table_exists = cursor.fetchone()

    if not table_exists:
        print("Creating database schema...")
        cursor.execute('''
            CREATE TABLE requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_query TEXT NOT NULL,
                flowise_response TEXT NOT NULL,
                gemini_image_url_1 TEXT NOT NULL,
                gemini_image_url_2 TEXT NOT NULL
            )
        ''')
        conn.commit()
        print("Database schema created.")
    else:
        print("Database schema already exists.")
    conn.close()


def save_request_to_db(user_query, flowise_response, image_url_1, image_url_2):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO requests (user_query, flowise_response, gemini_image_url_1, gemini_image_url_2, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_query, flowise_response, image_url_1, image_url_2, datetime.datetime.now())) # Use datetime.datetime.now()
    db.commit()
    print(f"Saved to DB: {user_query}, {flowise_response}, {image_url_1}, {image_url_2}")


def get_all_archived_requests_from_db():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, timestamp, user_query, flowise_response, gemini_image_url_1, gemini_image_url_2 FROM requests ORDER BY timestamp DESC")
    requests_data = cursor.fetchall()
    # Convert Row objects to dictionaries for JSON serialization
    return [dict(row) for row in requests_data]

# --- Helper Functions for External APIs ---
import requests # Ensure requests is imported if not already at the top

def call_flowise_api(query_text):
    """
    Calls the configured Flowise API with the user's query.
    Returns the Flowise response text or None if an error occurs.
    """
    payload = {"question": query_text}
    headers = {}
    if FLOWISE_API_KEY:
        headers["Authorization"] = f"Bearer {FLOWISE_API_KEY}"
        # Note: Adjust if Flowise expects a different auth mechanism or key name

    print(f"Calling Flowise API at {FLOWISE_API_ENDPOINT} with query: {query_text}")
    try:
        response = requests.post(FLOWISE_API_ENDPOINT, json=payload, headers=headers, timeout=30) # Added timeout
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)

        # The structure of the Flowise response needs to be known to extract the relevant text.
        # Assuming the response JSON has a key like 'text', 'answer', or similar.
        # The user's example `response.json()` implies it's a JSON object.
        # Let's try to find a common key, or user might need to specify.
        # Common keys in Flowise responses might be 'text' or inside a 'data' object.
        # Based on the user's sample code: `output = query({"question": "Hey, how are you?"})`
        # and then `output` is the result. It's likely the direct JSON response is what's needed,
        # or a specific field within it.
        # For now, let's assume the response itself is a JSON where a 'text' or 'message' field might exist.
        # Or, as per Flowise documentation, it might be in `result.text` or `output.text` or just `text`.
        # Let's try a few common ones or return the whole JSON string if specific field is unknown.

        response_json = response.json()
        print(f"Flowise API Response JSON: {response_json}")

        # Attempt to extract text based on common Flowise patterns
        if "text" in response_json:
            return response_json["text"]
        elif "output" in response_json and isinstance(response_json["output"], str):
            return response_json["output"]
        elif "message" in response_json: # Another common pattern
            return response_json["message"]
        elif "answer" in response_json: # Yet another
            return response_json["answer"]
        else:
            # If no specific known key, return the full JSON as string, or indicate ambiguity.
            # This part may need adjustment based on actual Flowise setup.
            # For now, returning a string representation.
            # The user's example `return response.json()` suggests the whole object might be the "response"
            # but the requirement is for "textual response".
            print("Warning: Could not find a standard text field in Flowise response. Returning full JSON content.")
            return str(response_json) # Fallback, may need refinement

    except requests.exceptions.RequestException as e:
        print(f"Error calling Flowise API: {e}")
        return None
    except Exception as e: # Catch other potential errors like JSON decoding
        print(f"An unexpected error occurred during Flowise API call: {e}")
        return None

# --- API Endpoints ---

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/archive')
def serve_archive_page():
    return send_from_directory(app.static_folder, 'archive.html')

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(app.config['IMAGES_FOLDER'], filename)

@app.route('/api/process', methods=['POST'])
def process_request():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "Missing 'query' in request body"}), 400

    user_query = data['query']

    # 1. Call Flowise API
    flowise_response_text = call_flowise_api(user_query)
    if flowise_response_text is None:
        return jsonify({"error": "Failed to get response from Flowise API"}), 500

    # 2. Call Gemini (Placeholder - creates dummy images)
    # As per user confirmation, actual Gemini image generation will be added later.
    # For now, we use the Flowise response to generate dummy image names
    # and create placeholder files.
    print(f"Simulating Gemini call with prompt (from Flowise): {flowise_response_text}")

    # Create dummy image files for now
    # Use a portion of the flowise response for uniqueness, or a timestamp
    timestamp_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    dummy_image_name1 = f"gemini_image_1_{timestamp_id}.png"
    dummy_image_name2 = f"gemini_image_2_{timestamp_id}.png"
    dummy_image_path1 = os.path.join(app.config['IMAGES_FOLDER'], dummy_image_name1)
    dummy_image_path2 = os.path.join(app.config['IMAGES_FOLDER'], dummy_image_name2)

    # Create simple placeholder image files
    with open(dummy_image_path1, 'w') as f:
        f.write("This is a placeholder image 1.")
    with open(dummy_image_path2, 'w') as f:
        f.write("This is a placeholder image 2.")

    image_url_1 = f"/images/{dummy_image_name1}"
    image_url_2 = f"/images/{dummy_image_name2}"

    # 3. Save to Database (Placeholder)
    save_request_to_db(user_query, flowise_response_text, image_url_1, image_url_2)

    # 4. Respond to Frontend
    return jsonify({
        "flowiseResponse": flowise_response_text,
        "imageUrl1": image_url_1,
        "imageUrl2": image_url_2
    })

@app.route('/api/archive', methods=['GET'])
def get_archive():
    archived_requests = get_all_archived_requests_from_db() # Placeholder
    return jsonify(archived_requests)

if __name__ == '__main__':
    init_db_schema() # Initialize DB schema on startup
    # For development, ensure API keys are set or provide defaults/warnings
    if not FLOWISE_API_KEY:
        print("Warning: FLOWISE_API_KEY environment variable is not set.")
    if not GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY environment variable is not set.")

    app.run(debug=True, host='0.0.0.0', port=5000)

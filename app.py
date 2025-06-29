from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import sqlite3
import datetime
import os
import config  # Import the configuration

# --- App Initialization ---
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app) # Enable CORS for all routes

# --- Database Configuration ---
DATABASE = config.DATABASE_NAME

# --- Database Helper Functions ---
def get_db_connection():
    """Connects to the specific database."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row # This allows accessing columns by name
    return conn

def init_db(app_context=None):
    """Initializes the database and creates the 'concetti' table if it doesn't exist."""
    # If app_context is provided, use it, otherwise create a new app context
    # This is useful for calling init_db from outside a request context (e.g., CLI)
    if app_context:
        with app_context:
            conn = get_db_connection()
            try:
                with conn: # Context manager for commit/rollback
                    cursor = conn.cursor()
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS concetti (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            prompt_utente TEXT NOT NULL,
                            descrizione_testuale TEXT NOT NULL,
                            url_immagine_1 TEXT,
                            url_immagine_2 TEXT,
                            data_creazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    print(f"Database '{DATABASE}' initialized and 'concetti' table ensured.")
            except sqlite3.Error as e:
                print(f"Error initializing database: {e}")
            finally:
                if conn:
                    conn.close()
    else: # Fallback for direct script execution without Flask app context
        conn = get_db_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS concetti (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        prompt_utente TEXT NOT NULL,
                        descrizione_testuale TEXT NOT NULL,
                        url_immagine_1 TEXT,
                        url_immagine_2 TEXT,
                        data_creazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                print(f"Database '{DATABASE}' initialized and 'concetti' table ensured (no app context).")
        except sqlite3.Error as e:
            print(f"Error initializing database (no app context): {e}")
        finally:
            if conn:
                conn.close()


# Command to initialize DB from CLI: flask init-db
@app.cli.command('init-db')
def init_db_command():
    """Clear existing data and create new tables."""
    init_db(app.app_context()) # Pass the application context
    print('Initialized the database.')


# --- Static File Serving (to be refined in Step 5) ---
@app.route('/')
def serve_index():
    # This will serve index.html from the 'templates' folder.
    # We'll create a dummy index.html for now.
    return render_template('index.html')

@app.route('/archive')
def serve_archive_page():
    # This will serve archive.html from the 'templates' folder.
    # We'll create a dummy archive.html for now.
    return render_template('archive.html')

# Flask automatically serves files from the 'static_folder' (set to 'static' in Flask app definition)
# at the '/static' URL path. For example, if you have a file static/style.css,
# it will be available at your_app_url/static/style.css.
# The previous route @app.route('/<path:filename>') was too broad and has been removed.
# Ensure your HTML files reference static assets like: <link rel="stylesheet" href="/static/style.css">


import requests # Added for actual API calls later, good to have it imported
import google.generativeai as genai # Added for actual API calls later

# --- API Endpoints (to be implemented) ---

# --- Placeholder/Simulated API Call Functions ---
def call_flowise_api_mock(prompt_text):
    """
    Mocks a call to the Flowise API.
    In a real scenario, this would make an HTTP request to config.PLACEHOLDER_FLOWISE_API_URL.
    """
    print(f"Mock Flowise API called with prompt: {prompt_text}")
    # Simulate Flowise response structure
    return {
        "risposta_testuale": f"Questa è una descrizione generata da Flowise (mock) per il prompt: '{prompt_text}'. Contiene dettagli e specifiche.",
        "istruzioni_immagini": [
            f"Prompt immagine 1 basato su: {prompt_text}",
            f"Prompt immagine 2 basato su: {prompt_text}"
        ]
    }

def call_gemini_api_mock(image_prompt):
    """
    Mocks a call to the Gemini API for image generation.
    In a real scenario, this would use the google-generativeai library.
    """
    print(f"Mock Gemini API called for image prompt: {image_prompt}")
    # Simulate Gemini returning a public URL for the generated image
    # Replace with a more realistic placeholder if needed, e.g., from a placeholder image service
    return f"https://via.placeholder.com/800x600.png?text=Immagine+per+{image_prompt.replace(' ', '+')}"

# --- Actual API Endpoint Implementations ---

# --- App-level Error Handlers for JSON responses ---
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Risorsa non trovata."}), 404

@app.errorhandler(500)
def internal_error(error):
    # Log the error for server-side debugging
    print(f"Errore interno del server: {error}")
    return jsonify({"error": "Errore interno del server."}), 500

@app.errorhandler(400)
def bad_request_error(error):
    # This can be triggered by request.abort(400) or Flask's own checks
    # error.description often contains a useful message from Flask.
    message = error.description if hasattr(error, 'description') and error.description else "Richiesta non valida."
    return jsonify({"error": message}), 400


@app.route('/api/generate', methods=['POST'])
def api_generate_concept():
    """
    Endpoint to generate a new concept.
    It takes a user prompt, calls Flowise, then calls Gemini for images.
    """
    if not request.is_json:
        return jsonify({"error": "Richiesta non valida, JSON atteso."}), 400

    data = request.get_json()
    user_prompt = data.get('prompt')

    if not user_prompt:
        return jsonify({"error": "Il campo 'prompt' è obbligatorio."}), 400

    try:
        # 1. Call Flowise API (mocked for now)
        flowise_response = call_flowise_api_mock(user_prompt)

        descrizione_testuale = flowise_response.get("risposta_testuale")
        istruzioni_immagini = flowise_response.get("istruzioni_immagini")

        if not descrizione_testuale or not istruzioni_immagini or not isinstance(istruzioni_immagini, list):
            # Log this error on the server for more details
            print(f"Errore: Risposta da Flowise (mock) non valida: {flowise_response}")
            return jsonify({"error": "Errore nell'elaborazione della risposta da Flowise (mock)."}), 500

        # 2. Call Gemini API for each image instruction (mocked for now)
        image_urls = []
        if len(istruzioni_immagini) >= 2: # Ensure we have at least two image prompts
            for i in range(2): # Generate two images
                image_prompt = istruzioni_immagini[i]
                image_url = call_gemini_api_mock(image_prompt)
                if image_url:
                    image_urls.append(image_url)
                else:
                    # Log this error as well
                    print(f"Errore: Gemini (mock) non ha restituito un URL per il prompt: {image_prompt}")
                    # Decide if we should proceed with fewer images or fail
                    # For now, we'll try to append what we get
                    pass # Or append a placeholder error image URL
        else:
            print(f"Avviso: Flowise (mock) ha restituito meno di 2 istruzioni per immagini: {istruzioni_immagini}")
            # Handle cases with fewer than 2 image prompts if necessary, e.g., by returning fewer images
            # For now, if not enough prompts, image_urls might be shorter than 2.

        # 3. Construct the final response
        response_data = {
            "descrizione": descrizione_testuale,
            "immagini": image_urls
        }

        return jsonify(response_data), 200

    except Exception as e:
        # Log the full error for debugging
        print(f"Errore imprevisto in /api/generate: {str(e)}")
        return jsonify({"error": "Errore interno del server durante la generazione del concept."}), 500


@app.route('/api/archive', methods=['GET', 'POST'])
def api_manage_archive():
    if request.method == 'GET':
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, prompt_utente, descrizione_testuale, url_immagine_1, url_immagine_2, data_creazione FROM concetti ORDER BY data_creazione DESC")
            concepts = cursor.fetchall()
            conn.close()
            # Convert list of Row objects to list of dicts for JSON serialization
            return jsonify([dict(concept) for concept in concepts]), 200
        except sqlite3.Error as e:
            print(f"Database error in GET /api/archive: {e}")
            return jsonify({"error": "Errore nel recupero dei dati dall'archivio."}), 500
        except Exception as e:
            print(f"Unexpected error in GET /api/archive: {e}")
            return jsonify({"error": "Errore interno del server."}), 500

    elif request.method == 'POST':
        if not request.is_json:
            return jsonify({"error": "Richiesta non valida, JSON atteso."}), 400

        data = request.get_json()
        prompt_utente = data.get('prompt_utente')
        descrizione_testuale = data.get('descrizione_testuale')
        url_immagine_1 = data.get('url_immagine_1')
        url_immagine_2 = data.get('url_immagine_2') # Optional, might not always be present

        if not all([prompt_utente, descrizione_testuale, url_immagine_1]): # url_immagine_2 is optional
            return jsonify({"error": "Dati mancanti. 'prompt_utente', 'descrizione_testuale', 'url_immagine_1' sono obbligatori."}), 400

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO concetti (prompt_utente, descrizione_testuale, url_immagine_1, url_immagine_2) VALUES (?, ?, ?, ?)",
                (prompt_utente, descrizione_testuale, url_immagine_1, url_immagine_2 if url_immagine_2 else None) # Handle optional image 2
            )
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            return jsonify({"status": "success", "id": new_id}), 201
        except sqlite3.Error as e:
            print(f"Database error in POST /api/archive: {e}")
            return jsonify({"error": "Errore nel salvataggio del concept nell'archivio."}), 500
        except Exception as e:
            print(f"Unexpected error in POST /api/archive: {e}")
            return jsonify({"error": "Errore interno del server."}), 500

# --- Main Execution ---
if __name__ == '__main__':
    # It's good practice to ensure the DB is initialized when the app starts,
    # but for CLI-based initialization, we might call init_db() separately.
    # For now, let's assume manual initialization or a separate script.
    # init_db() # Call this if you want to auto-initialize on startup

    # Instructions to run:
    # 1. Make sure you have all packages from requirements.txt installed.
    #    (e.g., pip install -r requirements.txt)
    # 2. Set environment variables or update config.py with your API keys/URLs.
    # 3. Initialize the database (first time setup):
    #    In your terminal, run: flask init-db
    # 4. Run the Flask app:
    #    flask run
    #    For development with auto-reload: app.run(debug=True, port=5000)
    app.run(debug=True, port=5000)

# ConceptGen Edilizia - Backend

This is the Flask backend for the ConceptGen Edilizia application. It handles user requests, interacts with Flowise to generate text concepts, (currently) simulates image generation with Gemini, and archives the results in an SQLite database.

## Features

- Serves frontend static files (`index.html`, `archive.html`).
- API endpoint (`/api/process`) to:
    - Receive a user's textual query.
    - Call a Flowise API to process the query and get a textual response.
    - Simulate Gemini image generation based on the Flowise response (creates placeholder image files).
    - Save the user query, Flowise response, and image URLs to an SQLite database.
    - Return the Flowise response and image URLs to the frontend.
- API endpoint (`/api/archive`) to retrieve all archived requests.
- Serves generated (placeholder) images.

## Project Structure

```
.
├── app.py                  # Main Flask application, API endpoints, core logic
├── init_db_command.py      # Script to manually initialize the database
├── requirements.txt        # Python dependencies
├── static/                 # Folder for static frontend files
│   ├── index.html
│   └── archive.html
├── images/                 # Folder where (placeholder) generated images are stored
├── archive.db              # SQLite database file (created automatically or by init_db_command.py)
└── README.md               # This file (should be this backend README)
```

## Setup and Installation

1.  **Clone the repository (or set up project files):**
    If this backend is part of a larger repository, ensure all files (`app.py`, `init_db_command.py`, `requirements.txt`, `static/`, `images/`) are in place.

2.  **Create a Python Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Environment Variables:**
    The application requires the following environment variables to be set. You can set them in your shell, or using a `.env` file (if you use a library like `python-dotenv`, which is not included by default).

    *   `FLOWISE_API_ENDPOINT`: The full URL of your Flowise API.
        *   Example: `export FLOWISE_API_ENDPOINT="http://your-flowise-instance/api/v1/prediction/your-flow-id"`
        *   If not set, the application will default to `http://192.168.1.122:8009/api/v1/prediction/e336ac20-fc71-4d17-baeb-1db07480de2d`.
    *   `FLOWISE_API_KEY`: (Optional) Your Flowise API key, if your Flowise endpoint requires authentication.
        *   Example: `export FLOWISE_API_KEY="your_flowise_api_key"`
    *   `GEMINI_API_KEY`: Your Google Gemini API key. (Currently only used for placeholder identification, but essential for future real integration).
        *   Example: `export GEMINI_API_KEY="your_gemini_api_key"`

    **Note on Gemini:** Currently, Gemini integration for image generation is a placeholder. You will need to replace the placeholder logic in `app.py` with actual calls to a Gemini image generation API (e.g., using Vertex AI Imagen) when ready.

5.  **Initialize the Database:**
    The database schema is created automatically when `app.py` is first run.
    Alternatively, you can initialize the database manually by running:
    ```bash
    python init_db_command.py
    ```
    This will create the `archive.db` file and the `requests` table if they don't already exist.

## Running the Application

1.  **Ensure all environment variables are set** as described above.
2.  **Activate your virtual environment** (if you created one).
3.  **Run the Flask application:**
    ```bash
    python app.py
    ```
    The application will start, typically on `http://0.0.0.0:5000/` or `http://127.0.0.1:5000/`.
    You should see output indicating the server is running, and whether the database schema was created or already existed.
    Warnings will be printed if API keys are not set.

## API Endpoints

*   **`GET /`**: Serves the main page (`index.html`).
*   **`GET /archive`**: Serves the archive page (`archive.html`).
*   **`POST /api/process`**:
    *   **Request Body (JSON):** `{ "query": "your text prompt" }`
    *   **Response (JSON):** `{ "flowiseResponse": "...", "imageUrl1": "/images/...", "imageUrl2": "/images/..." }`
    *   Handles the main processing flow: calls Flowise, (simulates) Gemini, saves to DB.
*   **`GET /api/archive`**:
    *   **Response (JSON):** `[ { "id": 1, "timestamp": "...", "user_query": "...", ... }, ... ]`
    *   Returns all entries from the archive database.
*   **`GET /images/<image_name>`**: Serves the specified image from the `images` folder.

## Deployment (Example for Google Cloud Run)

This application is a standard Flask app and can be deployed to various platforms like Google Cloud Run, Heroku, AWS Elastic Beanstalk, etc.

For **Google Cloud Run**:

1.  **Dockerfile:** Create a `Dockerfile` in your project root:
    ```dockerfile
    # Use an official Python runtime as a parent image
    FROM python:3.9-slim

    # Set the working directory in the container
    WORKDIR /app

    # Copy the dependencies file to the working directory
    COPY requirements.txt .

    # Install any needed packages specified in requirements.txt
    RUN pip install --no-cache-dir -r requirements.txt

    # Copy the rest of the application code to the working directory
    COPY . .

    # Make port 8080 available to the world outside this container
    # Cloud Run expects the container to listen on the port defined by the PORT env var (defaults to 8080)
    ENV PORT 8080

    # Define environment variable for Flask app (optional, can be set in Cloud Run service)
    # ENV FLASK_APP app.py

    # Run app.py when the container launches
    # Use gunicorn for a production-ready server
    CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
    ```
    You might need to add `gunicorn` to your `requirements.txt`.

2.  **`requirements.txt`:** Ensure `gunicorn` is added:
    ```
    Flask>=2.0
    requests>=2.20
    google-generativeai>=0.3.0
    Pillow>=9.0
    gunicorn>=20.0
    ```
    Then run `pip install -r requirements.txt` locally to update your environment if needed.

3.  **Build and Push to Google Container Registry (or Artifact Registry):**
    ```bash
    gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/conceptgen-backend
    ```
    Replace `YOUR_PROJECT_ID` with your Google Cloud Project ID.

4.  **Deploy to Cloud Run:**
    ```bash
    gcloud run deploy conceptgen-backend-service \
        --image gcr.io/YOUR_PROJECT_ID/conceptgen-backend \
        --platform managed \
        --region YOUR_REGION \
        --allow-unauthenticated \
        --set-env-vars FLOWISE_API_ENDPOINT="YOUR_FLOWISE_ENDPOINT_URL" \
        --set-env-vars FLOWISE_API_KEY="YOUR_FLOWISE_KEY" \
        --set-env-vars GEMINI_API_KEY="YOUR_GEMINI_KEY"
    ```
    - Replace `YOUR_PROJECT_ID`, `YOUR_REGION`, and the environment variable values accordingly.
    - `--allow-unauthenticated` makes the service publicly accessible. Adjust as needed.
    - Cloud Run will inject a `PORT` environment variable (defaulting to 8080), which Gunicorn will use.

5.  **Database on Cloud Run:**
    - SQLite (`archive.db`) is file-based. On Cloud Run's default ephemeral filesystem, the database will be lost if the instance restarts.
    - For persistent storage on Cloud Run, you should:
        - Use **Cloud SQL** (PostgreSQL, MySQL, SQL Server) as your database. This requires modifying `app.py` to use a different database connector (e.g., `psycopg2-binary` for PostgreSQL) and connection string.
        - Or, use another managed database service.

## Further Development

*   **Implement Real Gemini Image Generation:** Replace the placeholder image generation logic in `app.py` with actual calls to your chosen Gemini/Imagen API. This will likely involve using a library like `google-cloud-aiplatform`.
*   **Refine Flowise Response Parsing:** The `call_flowise_api` function in `app.py` attempts to extract text from common fields in the Flowise JSON response. This may need adjustment based on the specific structure of your Flowise flow's output.
*   **Error Handling and Logging:** Enhance error handling and add more robust logging for production.
*   **Security:** Review security best practices, especially for API key management and input validation if exposing this publicly.
*   **Frontend Integration:** Ensure the frontend JavaScript correctly calls the `/api/process` and `/api/archive` endpoints and handles the responses.
```

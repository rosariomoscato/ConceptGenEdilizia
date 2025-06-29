# ConceptGen Edilizia WebApp

## Project Overview

ConceptGen Edilizia is a web application designed for creating concept designs for the construction industry. Users can input a textual prompt describing their infrastructure concept. The application then processes this prompt using Flowise to refine or expand on the concept, and subsequently uses Gemini (currently placeholder) to generate visualizations based on the processed text. Generated concepts (text and images) can be saved to a local SQLite database and viewed in an archive.

This project uses a Python Flask backend and plain HTML, CSS, and JavaScript for the frontend.

## Features

-   **Concept Generation**: User inputs a text prompt to generate a detailed concept and accompanying images.
-   **Flowise Integration**: Leverages a Flowise instance to process and elaborate on the user's initial prompt.
-   **Gemini Image Generation**: Integrates with Gemini (currently a placeholder) to create visual representations of the concept.
-   **Archive System**: Allows users to save generated concepts (text and image URLs) to a local SQLite database.
-   **View Archive**: Users can browse previously saved concepts.
-   **Copy to Clipboard**: Easily copy the generated textual concept.

## Tech Stack

-   **Backend**: Python, Flask
-   **Frontend**: HTML, TailwindCSS, JavaScript
-   **Database**: SQLite
-   **AI Services**:
    -   Flowise (for text processing/generation)
    -   Gemini (for image generation - currently placeholder)

## Project Structure

```
.
├── backend/
│   ├── app.py              # Main Flask application, API endpoints
│   ├── database.py         # SQLite database setup and helper functions
│   ├── requirements.txt    # Python backend dependencies
│   └── database.db         # SQLite database file (created on first run)
├── static/
│   ├── css/
│   │   └── style.css       # Custom CSS styles
│   ├── js/
│   │   ├── main.js         # JavaScript for index.html
│   │   └── archive.js      # JavaScript for archive.html
│   └── images/             # For any static images (if needed)
├── .gitignore              # Specifies intentionally untracked files
├── archive.html            # Frontend for viewing archived concepts
├── index.html              # Main frontend page for generating concepts
└── README.md               # This file
```

## Prerequisites

-   Python 3.7+
-   `pip` (Python package installer)
-   Access to a Flowise instance (URL and Bearer Token)
-   (Eventually) Gemini API Key and relevant endpoint information.

## Setup and Running the Project

1.  **Clone the Repository**:
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Backend Setup**:

    *   **Navigate to the backend directory**:
        ```bash
        cd backend
        ```

    *   **Create a Python virtual environment** (recommended):
        ```bash
        python -m venv venv
        ```
        Activate the virtual environment:
        -   On Windows: `venv\\Scripts\\activate`
        -   On macOS/Linux: `source venv/bin/activate`

    *   **Install dependencies**:
        ```bash
        pip install -r requirements.txt
        ```
        If you plan to implement the actual Gemini integration, you will also need to install `google-generativeai`:
        ```bash
        pip install google-generativeai
        ```

    *   **Configure Environment Variables**:
        The application uses environment variables for API keys and Flowise configuration. You can set these directly in your shell, or create a `.env` file in the `backend` directory (and ensure `.env` is in your `.gitignore`).
        If using a `.env` file, you might want to add `python-dotenv` to `requirements.txt` and load it in `app.py`. For simplicity, this guide assumes direct environment variable setting.

        **Required for Flowise:**
        ```bash
        export FLOWISE_API_URL="YOUR_FLOWISE_INSTANCE_URL"
        # e.g., "http://192.168.1.122:8009/api/v1/prediction/your-flow-id"
        export FLOWISE_BEARER_TOKEN="YOUR_FLOWISE_BEARER_TOKEN"
        # e.g., "iZizq9uRxPLzc9rHfL-bXevYxPfoMiLwf5tcu8SKShw"
        ```
        Replace placeholder values with your actual Flowise endpoint and token.

        **Placeholders for Gemini (update when implementing):**
        ```bash
        export GEMINI_API_KEY="YOUR_GEMINI_API_KEY_PLACEHOLDER"
        export GEMINI_API_ENDPOINT="YOUR_GEMINI_API_ENDPOINT_PLACEHOLDER"
        ```
        Update these when you integrate the actual Gemini API. The `GEMINI_API_ENDPOINT` is not actively used by the current placeholder code but is good practice to have.

    *   **Initialize the Database**:
        The database and `concepts` table will be created automatically when `app.py` is first run. You can also initialize it manually if needed by running `python database.py` from the `backend` directory.

    *   **Run the Flask Application**:
        Ensure you are in the `backend` directory and your virtual environment is active.
        ```bash
        python app.py
        ```
        The backend server will start, typically on `http://127.0.0.1:5001`. Output in the console will confirm the address.

3.  **Frontend Access**:

    *   Open your web browser and navigate to the main page:
        [http://127.0.0.1:5001/](http://127.0.0.1:5001/)
        or
        [http://127.0.0.1:5001/index.html](http://127.0.0.1:5001/index.html)

    *   The archive page can be accessed via the "Archive" button on the main page or directly at:
        [http://127.0.0.1:5001/archive.html](http://127.0.0.1:5001/archive.html)

## Development Notes

-   **Gemini Placeholder**: The `generate_images_with_gemini` function in `backend/app.py` is currently a placeholder. It simulates an API call and returns static image URLs. Refer to the comments within this function for instructions on integrating the actual Gemini API.
-   **Error Handling**: Basic error handling is implemented on both frontend and backend. Check browser console and Flask server logs for debugging.
-   **Styling**: TailwindCSS is used for styling. Custom global styles can be added to `static/css/style.css`.

## Deployment (Basic Guidance)

For production, the Flask development server (`app.run()`) is not suitable. Consider using a production-ready WSGI server like Gunicorn or uWSGI, often in conjunction with a reverse proxy like Nginx.

**Example with Gunicorn:**

1.  Install Gunicorn:
    ```bash
    pip install gunicorn
    ```
2.  Run the app with Gunicorn (from the `backend` directory):
    ```bash
    gunicorn -w 4 -b 0.0.0.0:5001 app:app
    ```
    (Adjust `-w` (workers) and `-b` (bind address) as needed.)

Dockerizing the application would be another common step for easier deployment and scaling. This would involve creating a `Dockerfile` to package the backend and its dependencies. The frontend (HTML/JS/CSS) is served as static files by Flask in this setup, so it would be included in the Docker image or served by a separate web server/CDN in more complex setups.

---

This README provides a comprehensive guide to understanding, setting up, and running the ConceptGen Edilizia web application.

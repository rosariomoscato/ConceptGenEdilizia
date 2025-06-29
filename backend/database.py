import sqlite3
import json

DATABASE_NAME = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database and creates the 'concepts' table if it doesn't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS concepts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT NOT NULL,
            flowise_response TEXT,
            gemini_image_urls TEXT, -- Store as JSON string for multiple URLs
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized.")

def add_concept_to_archive(prompt, flowise_response, gemini_image_urls):
    """Adds a new concept to the archive."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Ensure gemini_image_urls is stored as a JSON string
        image_urls_json = json.dumps(gemini_image_urls)
        cursor.execute(
            "INSERT INTO concepts (prompt, flowise_response, gemini_image_urls) VALUES (?, ?, ?)",
            (prompt, flowise_response, image_urls_json)
        )
        conn.commit()
        concept_id = cursor.lastrowid
        print(f"Archived concept with ID: {concept_id}")
        return concept_id
    except sqlite3.Error as e:
        print(f"Database error in add_concept_to_archive: {e}")
        return None
    finally:
        conn.close()

def get_all_archived_concepts():
    """Retrieves all concepts from the archive, ordered by timestamp descending."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, prompt, flowise_response, gemini_image_urls, timestamp FROM concepts ORDER BY timestamp DESC")
        concepts_rows = cursor.fetchall()

        archived_items = []
        for row in concepts_rows:
            item = dict(row)
            # Parse the JSON string for image URLs back into a list
            item['gemini_image_urls'] = json.loads(item['gemini_image_urls']) if item['gemini_image_urls'] else []
            archived_items.append(item)
        return archived_items
    except sqlite3.Error as e:
        print(f"Database error in get_all_archived_concepts: {e}")
        return []
    finally:
        conn.close()

if __name__ == '__main__':
    # This can be run directly to initialize the database: python backend/database.py
    init_db()

    # Example usage (optional, for testing):
    # print("Attempting to add a dummy concept...")
    # test_prompt = "Test prompt for a futuristic city"
    # test_flowise = "This is a detailed description of a futuristic city with flying cars and tall skyscrapers."
    # test_images = ["http://example.com/image1.jpg", "http://example.com/image2.jpg"]
    # new_id = add_concept_to_archive(test_prompt, test_flowise, test_images)
    # if new_id:
    #     print(f"Added test concept with ID: {new_id}")

    # print("\nFetching all concepts:")
    # all_concepts = get_all_archived_concepts()
    # if all_concepts:
    #     for concept in all_concepts:
    #         print(f"ID: {concept['id']}, Prompt: {concept['prompt'][:30]}..., Images: {len(concept['gemini_image_urls'])}")
    # else:
    #     print("No concepts in archive or error fetching.")

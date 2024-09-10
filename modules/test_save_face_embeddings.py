import os
import sqlite3
import json
from deepface import DeepFace

# Set the directory where your images are stored
images_dir = "face_recognition/faces/030326"  # Change this to your image directory

# Database setup
db_file = "face_embeddings.db"  # SQLite database file


def create_db():
    """Create the SQLite database and table if it doesn't exist"""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table to store image embeddings
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS face_embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_path TEXT UNIQUE,
            embedding TEXT
        )
    """
    )

    conn.commit()
    conn.close()


def save_embedding_to_db(image_path, embedding_json):
    """Save the image path and its embedding to the SQLite database"""
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Insert the image path and its embedding
        cursor.execute(
            """
            INSERT OR REPLACE INTO face_embeddings (image_path, embedding)
            VALUES (?, ?)
        """,
            (image_path, embedding_json),
        )

        conn.commit()
        conn.close()

        print(f"Saved embedding for {image_path}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")


def embedding_exists(image_path):
    """Check if the embedding already exists in the database"""
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Check if the image path exists in the database
        cursor.execute(
            "SELECT COUNT(1) FROM face_embeddings WHERE image_path = ?", (image_path,)
        )
        exists = cursor.fetchone()[0] > 0

        conn.close()
        return exists

    except sqlite3.Error as e:
        print(f"Database error during existence check: {e}")
        return False


def process_existing_images(directory):
    """Process all existing images in the specified directory and store embeddings in DB"""
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        # Check if the file is an image
        if filename.endswith((".png", ".jpg", ".jpeg")):
            print(f"Processing image: {file_path}")

            # Check if embedding for this image already exists in the database
            if embedding_exists(filename):
                print(f"Skipping {file_path}, embedding already exists.")
                continue

            try:
                # Extract the face embedding using DeepFace (use Facenet512 for consistency)
                embedding = DeepFace.represent(
                    img_path=file_path, model_name="Facenet512", enforce_detection=False
                )

                # Convert the embedding to JSON format for storing in the database
                embedding_json = json.dumps(embedding)

                # Save the embedding to the database
                save_embedding_to_db(filename, embedding_json)

            except Exception as e:
                print(f"Error processing image {file_path}: {e}")


if __name__ == "__main__":
    # Create the database and table if it doesn't exist
    create_db()

    # Check if the directory exists
    if os.path.exists(images_dir):
        process_existing_images(images_dir)
    else:
        print(f"Directory {images_dir} does not exist.")

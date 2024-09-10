import sqlite3
import os
import json
from deepface import DeepFace
from flask import jsonify

class FaceEmbeddingDB:
    def __init__(self, db_file="face_embeddings.db"):
        self.db_file = db_file
        self.create_db()

    def create_db(self):
        """Create the SQLite database and table if it doesn't exist."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        # Create table to store subscription codes and image embeddings
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS face_embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subscription_code TEXT,
                embedding_name TEXT UNIQUE,
                embedding TEXT
            )
            """
        )
        conn.commit()
        conn.close()

    def save_embedding_to_db(self, subscription_code, embedding_name, embedding_json):
        """Save the subscription code, embedding name and embedding to the SQLite database."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            # Insert the subscription code, embedding name, and its embedding
            cursor.execute(
                """
                INSERT OR REPLACE INTO face_embeddings (subscription_code, embedding_name, embedding)
                VALUES (?, ?, ?)
                """,
                (subscription_code, embedding_name, embedding_json),
            )

            conn.commit()
            conn.close()

        except sqlite3.Error as e:
            print(f"Database error: {e}")

    def embedding_exists(self, embedding_name):
        """Check if the embedding already exists in the database."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT COUNT(1) FROM face_embeddings WHERE embedding_name = ?", (embedding_name,)
            )
            exists = cursor.fetchone()[0] > 0

            conn.close()
            return exists

        except sqlite3.Error as e:
            print(f"Database error during existence check: {e}")
            return False

    def process_image(self, file_path, subscription_code, side, registered_name):
        """Process an image and save its embedding to the database."""
        if registered_name:
            embeddings_name = f"{registered_name}_{side}"  # Use registered name in embedding
        else:
            filename = os.path.basename(file_path)
            embeddings_name = f"{filename.rsplit('.', 1)[0]}_{side}"

        # Check if embedding already exists
        if self.embedding_exists(embeddings_name):
            print(f"Embedding for {embeddings_name} already exists.")
            return jsonify({'success': False, 'message': 'Image already exists'})

        try:
            print(f"Processing image: {file_path} for subscription code: {subscription_code} and side: {side}")
            
            # Extract the face embedding using DeepFace
            embedding = DeepFace.represent(img_path=file_path, model_name="Facenet512", enforce_detection=False)
            embedding_json = json.dumps(embedding)
            
            # Save the embedding to the database
            self.save_embedding_to_db(subscription_code, embeddings_name, embedding_json)
            
            # Remove the original image after processing
            os.remove(file_path)

            return jsonify({'success': True, 'message': 'Embedding saved and image deleted'})

        except sqlite3.Error as db_error:
            print(f"Database error: {db_error}")
            return jsonify({'success': False, 'message': f"Database error: {db_error}"})

        except FileNotFoundError as fnf_error:
            print(f"File not found error: {fnf_error}")
            return jsonify({'success': False, 'message': f"File error: {fnf_error}"})

        except Exception as e:
            print(f"General error processing image {file_path}: {e}")
            return jsonify({'success': False, 'message': f"Error processing image: {e}"})

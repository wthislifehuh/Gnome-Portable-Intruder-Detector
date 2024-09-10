import sqlite3
import os
import re
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

    def process_images(self, file_paths, subscription_code):
        """Process the list of images and save their embeddings."""
        for file_path in file_paths:
            filename = os.path.basename(file_path)
            name = filename.rsplit('.', 1)[0]  # Use filename without extension as embedding name
            # Regex to find the last occurrence of _left, _right, or _middle
            pattern = r"(.*)_(left|right|middle)$"
            match = re.match(pattern, name)
            if match:
                # Get the name part before the last underscore
                name_part = match.group(1)
                # Remove any underscores from the name part
                cleaned_name = name_part.replace('_', ' ')
                # Combine the cleaned name with the suffix (_left, _right, _middle)
                embeddings_name = f"{cleaned_name}_{match.group(2)}"

            # Check if embedding already exists
            if self.embedding_exists(embeddings_name):
                print(f"Embedding for {embeddings_name} already exists.")
                continue

            try:
                print(f"Processing image: {file_path} for subscription code: {subscription_code}")
                
                # Extract the face embedding using DeepFace
                embedding = DeepFace.represent(img_path=file_path, model_name="Facenet512", enforce_detection=False)
                embedding_json = json.dumps(embedding)
                
                # Save the embedding to the database
                self.save_embedding_to_db(subscription_code, embeddings_name, embedding_json)
                
                # Remove the original image after processing
                os.remove(file_path)

            except Exception as e:
                print(f"Error processing image {file_path}: {e}")
                return jsonify({'success': False, 'message': f"Error processing image: {e}"})

        return jsonify({'success': True, 'message': 'Embeddings processed and images deleted'})

    def get_side_from_path(self, file_path):
        """Extract the side information (left, right, middle) from the file path."""
        if 'left' in file_path:
            return 'left'
        elif 'right' in file_path:
            return 'right'
        elif 'middle' in file_path:
            return 'middle'
        return 'unknown'


    def get_registered_persons(self, subscription_code):
            """Fetch and clean the names of registered persons from the database."""
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            # Retrieve embedding names for the specified subscription code
            cursor.execute(
                "SELECT embedding_name FROM face_embeddings WHERE subscription_code = ?", 
                (subscription_code,)
            )
            rows = cursor.fetchall()
            conn.close()

            # Extract and clean names (remove _left, _right, _middle)
            person_names = set()
            for row in rows:
                embedding_name = row[0]

                # Use regex to extract the person's name, removing side information
                match = re.match(r"(.*)_(left|right|middle)$", embedding_name)
                if match:
                    person_name = match.group(1).replace('_', ' ').title()  # Clean and format the name
                    person_names.add(person_name)

            return list(person_names)
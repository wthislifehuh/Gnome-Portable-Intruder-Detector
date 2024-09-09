

    
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
from database3 import SubscriptionManager
import sqlite3
import json
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from deepface import DeepFace
import base64
from io import BytesIO
from PIL import Image
import numpy as np

sub_manager = SubscriptionManager()

def validate_signUp():
    try:
        data = request.json
        subscription_code = data.get('subscriptionCode')
        telegram_chat_id = data.get('telegramChatID')
        password = data.get('password') 

        print(f"Received subscription code: {subscription_code}, Telegram chat ID: {telegram_chat_id}, Password: {password}")

        # Check if subscription code is valid
        if not sub_manager.verify_subscription_code(subscription_code):
            return jsonify({'success': False, 'message': 'Invalid subscription code'})
        
        # Verify password
        if not sub_manager.verify_password(subscription_code, password):
            return jsonify({'success': False, 'message': 'Incorrect password'})
        
        # Check if chat ID already exists, if not, add to the database
        if not sub_manager.verify_chat_id(telegram_chat_id):
            sub_manager.add_chat_id(subscription_code, telegram_chat_id)


        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': 'Server error'}), 500


def validate_signIn():
    try:
        data = request.json
        subscription_code = data.get('subscriptionCode')
        password = data.get('password')

        print(f"Received subscription code: {subscription_code}, Password: {password}")

        if not subscription_code or not password:
            return jsonify({'success': False, 'message': 'Missing subscription code or password'}), 400

        # Check if subscription code is valid
        if not sub_manager.verify_subscription_code(subscription_code):
            return jsonify({'success': False, 'message': 'Invalid subscription code'})

        # Verify password
        if not sub_manager.verify_password(subscription_code, password):
            return jsonify({'success': False, 'message': 'Incorrect password'})

        return jsonify({'success': True})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

def store_subscription_code():
    data = request.json
    subscription_code = data.get('subscriptionCode')

    if subscription_code:
        session['subscription_code'] = subscription_code  # Store in session
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'No subscription code provided'})


def remove_subscription_code():
    if 'subscription_code' in session:
        session.pop('subscription_code')  
        return jsonify({'success': True, 'message': 'Subscription code removed successfully'})
    return jsonify({'success': False, 'message': 'No subscription code found in session'})


# Route to add chatId
def add_chatID():
    data = request.json
    subscription_code = data.get('subscriptionCode')
    telegram_chat_id = data.get('telegramChatID')

    # Check if the chat ID already exists
    if sub_manager.verify_chat_id(telegram_chat_id):
        return jsonify({'success': False, 'message': 'ChatID has already registered.'})

    # Proceed with adding the new chat ID if it doesn't exist
    if sub_manager.add_chat_id(subscription_code, telegram_chat_id):
        return jsonify({'success': True, 'message': 'Chat ID added successfully'})
    else:
        return jsonify({'success': False, 'message': 'Error adding Chat ID'})
    

# Route to delete chatId
def delete_chatID():
    data = request.json
    subscription_code = data.get('subscriptionCode')
    telegram_chat_id = data.get('telegramChatID')

    # Check if the chat ID already exists
    if not sub_manager.verify_chat_id(telegram_chat_id):
        return jsonify({'success': False, 'message': 'ChatID does not exist.'})

    # Proceed with adding the new chat ID if it doesn't exist
    if sub_manager.delete_chat_id(subscription_code, telegram_chat_id):
        return jsonify({'success': True, 'message': 'Chat ID deleted successfully'})
    else:
        return jsonify({'success': False, 'message': 'Error adding Chat ID'})

# Route to update password
def update_password():
    data = request.json
    subscription_code = data.get('subscriptionCode')
    new_password = data.get('newPassword')

    if sub_manager.update_password(subscription_code, new_password):
        return jsonify({'success': True, 'message': 'Password updated successfully'})
    else:
        return jsonify({'success': False, 'message': 'Error updating password'})
    


# def upload_photo():
#     if 'file' not in request.files or 'subscriptionCode' not in request.form:
#         return jsonify({'success': False, 'message': 'No file or subscription code part'})

#     file = request.files['file']
#     subscription_code = request.form['subscriptionCode']  # Retrieve the subscription code
#     side = request.form['side']

#     if file.filename == '':
#         return jsonify({'success': False, 'message': 'No selected file'})

#     if file and subscription_code:
#         # Create the folder for the subscription if it doesn't exist
#         subscription_dir = os.path.join('face_recognition/faces', subscription_code)
#         os.makedirs(subscription_dir, exist_ok=True)

#         # Save the file in the subscription folder
#         filename = secure_filename(file.filename)
#         file.save(os.path.join(subscription_dir, filename))

#         return jsonify({'success': True})
#     else:
#         return jsonify({'success': False, 'message': 'File or subscription code missing'})
    

# ============================ Embeddings database ===================================================================
# Database setup
db_file = "face_embeddings.db"  # SQLite database file

def create_db():
    """Create the SQLite database and table if it doesn't exist"""
    conn = sqlite3.connect(db_file)
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

def save_embedding_to_db(subscription_code, embedding_name, embedding_json):
    """Save the subscription code, embedding name and embedding to the SQLite database"""
    try:
        conn = sqlite3.connect(db_file)
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


def process_image(file_path, subscription_code, side, registered_name):
    """Process an image and save its embedding to the database"""
    create_db()

    if registered_name:
        embeddings_name = f"{registered_name}_{side}"  # Use registered name in embedding
    else:
        filename = os.path.basename(file_path)
        embeddings_name = f"{filename.rsplit('.', 1)[0]}_{side}"

    # Check if embedding already exists
    if embedding_exists(embeddings_name):
        print(f"Embedding for {embeddings_name} already exists.")
        return jsonify({'success': False, 'message': 'Image already exists'})

    try:
        print(f"Processing image: {file_path} for subscription code: {subscription_code} and side: {side}")
        
        # Extract the face embedding using DeepFace
        embedding = DeepFace.represent(img_path=file_path, model_name="Facenet512", enforce_detection=False)
        embedding_json = json.dumps(embedding)
        # Save the embedding to the database
        save_embedding_to_db(subscription_code, embeddings_name, embedding_json)
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

def embedding_exists(embedding_name):
    """Check if the embedding already exists in the database"""
    try:
        conn = sqlite3.connect(db_file)
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

# Route to handle face photo uploads
def upload_photo():
    if 'file' not in request.files or 'subscriptionCode' not in request.form or 'side' not in request.form:
        return jsonify({'success': False, 'message': 'No file provided'})

    file = request.files['file']
    subscription_code = request.form['subscriptionCode']
    side = request.form['side']
    registered_name = request.form.get('registeredName', '').strip()

    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'})

    if file and subscription_code and side:
        subscription_dir = os.path.join('face_recognition/faces', subscription_code)
        os.makedirs(subscription_dir, exist_ok=True)

        filename = secure_filename(file.filename)
        file_path = os.path.join(subscription_dir, filename)
        file.save(file_path)

        # Pass registered name to process_image function
        return process_image(file_path, subscription_code, side, registered_name)
    else:
        return jsonify({'success': False, 'message': 'Missing required fields'})

# @app.route('/retrieve_image/<subscription_code>/<embedding_name>', methods=['GET'])
# def retrieve_image(subscription_code, embedding_name):
#     """Retrieve and decode the embedding, convert it back to an image, and serve it"""
#     try:
#         conn = sqlite3.connect(db_file)
#         cursor = conn.cursor()

#         cursor.execute(
#             "SELECT embedding FROM face_embeddings WHERE subscription_code = ? AND embedding_name = ?",
#             (subscription_code, embedding_name)
#         )
#         row = cursor.fetchone()

#         if row:
#             embedding_json = row[0]
#             embedding = json.loads(embedding_json)[0]['embedding']

#             # Convert embedding back to image (assuming embedding was an image, adjust this if necessary)
#             image_data = np.array(embedding).astype(np.uint8)
#             image = Image.fromarray(image_data)
#             buffer = BytesIO()
#             image.save(buffer, format="PNG")
#             encoded_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

#             conn.close()
#             return jsonify({'success': True, 'image': encoded_image})
#         else:
#             conn.close()
#             return jsonify({'success': False, 'message': 'Embedding not found'})

#     except sqlite3.Error as e:
#         return jsonify({'success': False, 'message': f'Database error: {e}'})
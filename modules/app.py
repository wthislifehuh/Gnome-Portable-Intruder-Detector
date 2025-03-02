

    
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
from database3 import SubscriptionManager
from embeddings import FaceEmbeddingDB
import json
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename


# Database setup
sub_manager = SubscriptionManager()
embedding = FaceEmbeddingDB()

# Route to validate sign up information
def validate_signUp():
    try:
        data = request.json
        subscription_code = data.get('subscriptionCode')
        telegram_chat_id = data.get('telegramChatID')
        password = data.get('password') 
        phoneNum = data.get('phoneNum')

        print(f"Received subscription code: {subscription_code}, Telegram chat ID: {telegram_chat_id}, Password: {password}, Phone Number: {phoneNum}")

        # Check if subscription code is valid
        if not sub_manager.verify_subscription_code(subscription_code):
            return jsonify({'success': False, 'message': 'Invalid subscription code'})
        
        # Verify password
        if not sub_manager.verify_password(subscription_code, password):
            return jsonify({'success': False, 'message': 'Incorrect password'})
        
        # Check if chat ID already exists, if not, add to the database
        if not sub_manager.verify_chatID_phoneNum(subscription_code, telegram_chat_id, phoneNum):
                sub_manager.add_chat_id(subscription_code, telegram_chat_id, phoneNum)

        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

# Route to validate sign in information
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
    phone_num = data.get('phone_num')

    # Check if the chat ID already exists
    if sub_manager.verify_chat_id(subscription_code, telegram_chat_id):
        return jsonify({'success': False, 'message': 'ChatID has already registered.'})
    
    if sub_manager.verify_chatID_phoneNum(subscription_code, telegram_chat_id, phone_num):
        return jsonify({'success': False, 'message': 'ChatID and phone number has already registered.'})

    # Proceed with adding the new chat ID if it doesn't exist
    if sub_manager.add_chat_id(subscription_code, telegram_chat_id, phone_num):
        return jsonify({'success': True, 'message': 'Chat ID and phone number added successfully'})
    else:
        return jsonify({'success': False, 'message': 'Error adding Chat ID'})
    

# Route to delete chatId
def delete_chatID():
    data = request.json
    subscription_code = data.get('subscriptionCode')
    telegram_chat_id = data.get('telegramChatID')

    # Check if the chat ID already exists
    if not sub_manager.verify_chat_id(subscription_code, telegram_chat_id):
        return jsonify({'success': False, 'message': 'ChatID does not exist.'})

    # Proceed with adding the new chat ID if it doesn't exist
    if sub_manager.delete_chat_id(subscription_code, telegram_chat_id):
        return jsonify({'success': True, 'message': 'Chat ID deleted successfully'})
    else:
        return jsonify({'success': False, 'message': 'Error adding Chat ID'})
    

# Route to update Phone Number
def update_phoneNum():
    data = request.json
    subscription_code = data.get('subscriptionCode')
    phone_num = data.get('phoneNum')
    chat_id = data.get('chat_id')

    print("In updating phone number:", subscription_code, phone_num, chat_id)
    # Check if the chat ID and phone number already exists
    if sub_manager.verify_chatID_phoneNum(subscription_code, chat_id, phone_num):
        return jsonify({'success': False, 'message': 'Phone Number has already registered.'})

    # Proceed with adding the new chat ID if it doesn't exist
    if sub_manager.update_phone_num_for_chat_id(subscription_code, chat_id,  phone_num):
        return jsonify({'success': True, 'message': 'Phone Number added successfully'})
    else:
        return jsonify({'success': False, 'message': 'Error adding phone number to Chat ID. Chat ID does not exist.'})
    
    


# Route to update password
def update_password():
    data = request.json
    subscription_code = data.get('subscriptionCode')
    new_password = data.get('newPassword')

    if sub_manager.update_password(subscription_code, new_password):
        return jsonify({'success': True, 'message': 'Password updated successfully'})
    else:
        return jsonify({'success': False, 'message': 'Error updating password'})
    


# ============================ Embeddings database ===================================================================

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
        # Define the storage directory
        subscription_dir = os.path.join('face_recognition/faces', subscription_code)
        os.makedirs(subscription_dir, exist_ok=True)

        # Construct the new filename using the registered name and side
        if registered_name:
            filename = f"{registered_name.replace(' ', '_')}_{side}.jpg"  # Replace spaces in the name
        else:
            filename = f"{secure_filename(file.filename.rsplit('.', 1)[0])}_{side}.jpg"

        file_path = os.path.join(subscription_dir, filename)
        file.save(file_path)

        # Return the uploaded file path without embedding processing
        return jsonify({'success': True, 'file_path': file_path})
    else:
        return jsonify({'success': False, 'message': 'Missing required fields'})


def process_embeddings():
    image_paths = json.loads(request.form['imagePaths'])
    subscription_code = request.form['subscriptionCode']

    if len(image_paths) != 3:
        return jsonify({'success': False, 'message': 'Incomplete image set for processing'})

    # Call the embedding function
    return embedding.process_images(image_paths, subscription_code)

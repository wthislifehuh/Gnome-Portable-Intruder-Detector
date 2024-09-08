
# from flask import Flask, request, jsonify
# from werkzeug.utils import secure_filename
# import os
# from modules.database3 import SubscriptionManager

# app = Flask(__name__)

# # Create instance of SubscriptionManager
# sub_manager = SubscriptionManager()

# # Validate subscription code and chat ID
# @app.route('/validate_subscription', methods=['POST'])

# def validate_subscription():
#     data = request.json
#     subscription_code = data.get('subscriptionCode')
#     telegram_chat_id = data.get('telegramChatID')

#     print(f"Received subscription code: {subscription_code}, Telegram chat ID: {telegram_chat_id}")

#     # Your existing validation logic
#     data = request.json
#     subscription_code = data.get('subscriptionCode')
#     telegram_chat_id = data.get('telegramChatID')

#     # Check if subscription code is valid
#     if not sub_manager.verify_subscription_code(subscription_code):
#         return jsonify({'success': False, 'message': 'Invalid subscription code'})

#     # Check if chat ID already exists, if not, add to the database
#     if not sub_manager.verify_chat_id(telegram_chat_id):
#         sub_manager.add_chat_id(subscription_code, telegram_chat_id)

#     return jsonify({'success': True})

# # Route to handle face photo uploads
# @app.route('/upload_photo', methods=['POST'])
# def upload_photo():
#     if 'file' not in request.files:
#         return jsonify({'success': False, 'message': 'No file part'})

#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({'success': False, 'message': 'No selected file'})

#     if file:
#         filename = secure_filename(file.filename)
#         file.save(os.path.join('face_recognition/faces/', filename))
#         return jsonify({'success': True})
    

    
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
from database3 import SubscriptionManager

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


# Route to update password
def update_password():
    data = request.json
    subscription_code = data.get('subscriptionCode')
    new_password = data.get('newPassword')

    if sub_manager.update_password(subscription_code, new_password):
        return jsonify({'success': True, 'message': 'Password updated successfully'})
    else:
        return jsonify({'success': False, 'message': 'Error updating password'})

# Route to handle face photo uploads
def upload_photo():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'})

    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join('face_recognition/faces/', filename))
        return jsonify({'success': True})
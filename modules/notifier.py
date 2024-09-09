# notifier.py
import os
import json
import requests
from dotenv import load_dotenv
from database2 import SubscriptionManager
from collections import Counter

class TelegramNotifier:
    def __init__(self, subscription_manager: SubscriptionManager):
        load_dotenv()
        self.token = os.getenv('BOT_TOKEN')
        if not self.token:
            raise ValueError("Bot token not found in environment variables.")
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.subscription_manager = subscription_manager

    def send_message(self, chat_id: str, message: str, reply_markup=None):
        url = f"{self.base_url}/sendMessage"
        params = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        if reply_markup:
            params["reply_markup"] = json.dumps(reply_markup)

        response = requests.get(url, params=params)
        if response.status_code == 200:
            print(f"Message sent successfully to chat_id {chat_id}.")
        else:
            print(f"Failed to send message to chat_id {chat_id}. Status code: {response.status_code}. Response: {response.json()}")
        return response

    async def send_notification(self, status):
        # Check if the status is a list of animals
        if isinstance(status, list):
            # Count occurrences of each animal
            animal_count = Counter(status)
            
            # Prepare a list to store formatted strings like '2 Dogs', '1 Cat', etc.
            formatted_status = []
            
            for animal, count in animal_count.items():
                # Capitalize the animal name and add plural form if count > 1
                animal_name = animal.capitalize() + ('s' if count > 1 else '')
                formatted_status.append(f"{count} {animal_name}")
            
            # Join the formatted strings with appropriate punctuation
            if len(formatted_status) == 2:
                # For two types of animals, join with "and"
                status = f"{formatted_status[0]} and {formatted_status[1]}"
            else:
                # For more than two types of animals, join with commas and "and" before the last one
                status = ', '.join(formatted_status[:-1]) + f", and {formatted_status[-1]}"
        else:
            # Capitalize the first letter if status is a single string
            status = status.capitalize()

        # Create the button list for the message
        button_list = [
            [{"text": "📺 Live Feeds", "callback_data": 'live_feed'}],
            [{"text": "📽️ Intruders Recording", "callback_data": 'recordings'}],
            [{"text": "📞 Emergency Contact", "callback_data": 'emergency'}],
        ]
        reply_markup = {"inline_keyboard": button_list}

        # Get all chat IDs from the subscription manager
        chat_ids = self.subscription_manager.get_all_chat_ids()

        # Send a notification to all chat IDs
        for chat_id in chat_ids:
            self.send_message(
                chat_id, 
                f"🚨Alert! {status} Intruders Detected! \nView the live feeds here or access the recordings of the intruders:", 
                reply_markup=reply_markup
            )


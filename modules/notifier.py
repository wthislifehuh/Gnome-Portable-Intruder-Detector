# notifier.py
import os
import json
import requests
from dotenv import load_dotenv
from database2 import SubscriptionManager

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

    def send_notification(self, status: str):
        # Capitalize the first letter of the status
        status = status.capitalize()

        button_list = [
            [{"text": "📺 Live Feeds", "callback_data": 'live_feed'}],
            [{"text": "📽️ Intruders Recording", "callback_data": 'recordings'}],
            [{"text": "📞 Emergency Contact", "callback_data": 'emergency'}],
        ]
        reply_markup = {"inline_keyboard": button_list}

        chat_ids = self.subscription_manager.get_all_chat_ids()

        for chat_id in chat_ids:
            if status == "Human" or status == "Dog":
                self.send_message(chat_id, f"🚨Alert! {status} Intruders Detected! \nView the live feeds here or access the recordings of the intruders:", reply_markup=reply_markup)
            elif status == "Low battery":
                self.send_message(chat_id, "⚠️ WARNING: Mobile battery Low! Check the condition of your device.")
            elif status == "Trigger":
                self.send_message(chat_id, "🚨 Alert! An event has been detected in the ROI!", reply_markup=reply_markup)
            elif status == "Warning":
                self.send_message(chat_id, "⚠️ WARNING: Unspecified alert!")


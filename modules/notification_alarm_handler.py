import asyncio
import requests
import aiohttp
import os
import json
from dotenv import load_dotenv
from database3 import SubscriptionManager
from collections import Counter
from twilio.rest import Client


class NotificationAlarmHandler:
    def __init__(self, channel):
        self.subscription = SubscriptionManager()
        self.event_url_map = {
            "human": "https://app.vybit.net/trigger/cc6ghxxta9zkdcd5",
            "dog": "https://vybit.net/trigger/2uqg0zrx9wof9jgx",
            "cat": "https://app.vybit.net/trigger/cc6ghxxta9zkdcd5"
        }
        load_dotenv()
        self.channel = channel  # Set the channel to subscription_code
        self.token = os.getenv('BOT_TOKEN')
        self.twilio_sid = os.getenv('TWILIO_SID')
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_number = os.getenv('TWILIO_NUMBER')

        if not self.token or not self.twilio_sid or not self.twilio_auth_token or not self.twilio_number:
            raise ValueError("Required environment variables not found.")

        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.twilio_client = Client(self.twilio_sid, self.twilio_auth_token)

    async def human_trigger(self, result):
        if len(result) > 1:
            await self.send_notification(result)
        else:
            await self.send_notification("human")
        await self.trigger_alarm("human")

    async def animal_trigger(self, animal):
        if len(animal) > 1:
            await self.send_notification(animal)  # Send notification for each animal
            await self.trigger_alarm("human")  # Trigger common alarm for multiple animals
        else:
            animal_type = animal[0]
            await self.send_notification(animal_type)  # Send notification for the single animal
            await self.trigger_alarm(animal_type)  # Trigger alarm specific to the animal

    async def trigger_alarm(self, event):
        url = self.event_url_map.get(event)
        if url:
            async with aiohttp.ClientSession() as session:
                async with session.post(url) as response:
                    print(f'Triggered {event} event with status: {response.status}')
        else:
            print(f"Unknown event: {event}")

    def send_message(self, chat_id: str, message: str, user_phone: str, reply_markup=None):
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
            return True  # Telegram message sent successfully
        else:
            print(f"Failed to send message to chat_id {chat_id}. Status code: {response.status_code}.")
            # Trigger SMS alert if Telegram message fails and phone number exists
            if user_phone:
                self.send_sms_alert(user_phone, message)
            return False  # Telegram message failed

    def send_sms_alert(self, phone_number, message):
        sms_message = self.twilio_client.messages.create(
            body=f"🚨 Alert! {message} Intruders Detected! Check your app for details.",
            from_=self.twilio_number,
            to=phone_number
        )
        print(f"SMS sent to {phone_number}, SID: {sms_message.sid}")

    async def send_notification(self, status):
        # Check if the status is a list of animals
        if isinstance(status, list):
            if all(item == 'Unknown' for item in status):
                human_count = len(status)
                status = "Human" if human_count == 1 else f"{human_count} Humans"
            else:
                if len(status) > 1:
                    animal_count = Counter(status)
                    formatted_status = [
                        f"{count} {animal.capitalize() + ('s' if count > 1 else '')}"
                        for animal, count in animal_count.items()
                    ]
                    if len(formatted_status) == 2:
                        status = f"{formatted_status[0]} and {formatted_status[1]}"
                    else:
                        status = ', '.join(formatted_status[:-1]) + f", and {formatted_status[-1]}"
                else:
                    status = status[0].capitalize()
        else:
            status = status.capitalize()

        # Prepare message and buttons
        button_list = [
            [{"text": "📺 Live Feeds", "callback_data": 'live_feed'}],
            [{"text": "📽️ Intruders Recording", "callback_data": 'recordings'}],
            [{"text": "📞 Emergency Contact", "callback_data": 'emergency'}],
        ]
        reply_markup = {"inline_keyboard": button_list}

        # Get all chat IDs and corresponding phone numbers from the subscription manager
        chat_id_phone_pairs = self.subscription.get_chat_ids_by_subscription_code(self.channel)

        # Send notifications to all users
        for chat in chat_id_phone_pairs:
            chat_id = chat['chat_id']
            phone_number = chat.get('phone_num', None)  # Get phone number or None if not available
            self.send_message(
                chat_id,
                f"🚨Alert! {status} Intruders Detected! \nView the live feeds here or access the recordings of the intruders:",
                user_phone=phone_number,
                reply_markup=reply_markup
            )

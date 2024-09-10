#noti_alarm_handler.py
import asyncio
import requests
import aiohttp
import asyncio
import os
import json
import requests
from dotenv import load_dotenv
from database3 import SubscriptionManager
from collections import Counter


class NotificationAlarmHandler:
    def __init__(self):
        self.subscription = SubscriptionManager()
        self.event_url_map = {
            "human": "https://app.vybit.net/trigger/cc6ghxxta9zkdcd5",
            "dog": "https://vybit.net/trigger/2uqg0zrx9wof9jgx",
            "cat": "https://app.vybit.net/trigger/cc6ghxxta9zkdcd5"
        }
        load_dotenv()
        self.token = os.getenv('BOT_TOKEN')
        if not self.token:
            raise ValueError("Bot token not found in environment variables.")
        self.base_url = f"https://api.telegram.org/bot{self.token}"

        
    async def human_trigger(self):
        await self.send_notification("human")
        await self.trigger_alarm("human")

    async def animal_trigger(self, animal):
        if len(animal) > 1:
            # Multiple animals, trigger common alarm, send notification for animals
            await self.send_notification(animal)  # Send notification for each animal
            await self.trigger_alarm("human")  # Trigger common alarm for multiple animals
            
        else:
            # Single animal, trigger specific alarm
            animal_type = animal[0]
            await self.send_notification(animal_type)  # Send notification for the single animal
            await self.trigger_alarm(animal_type)  # Trigger alarm specific to the animal

    async def trigger_alarm(self, event):
        """
        Trigger an alarm based on the event type.
        Parameters:
            event (str): The type of event to trigger (e.g., 'human', 'dog', 'cat').
        """
        url = self.event_url_map.get(event)
        if url:
            async with aiohttp.ClientSession() as session:
                async with session.post(url) as response:
                    print(f'Triggered {event} event with status: {response.status}')
        else:
            print(f"Unknown event: {event}")

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
            elif len(formatted_status) == 1:
                status = f"{formatted_status[0]}"
            else:
                # For more than two types of animals, join with commas and "and" before the last one
                status = ', '.join(formatted_status[:-1]) + f", and {formatted_status[-1]}"
        else:
            # Capitalize the first letter if status is a single string (human)
            status = status.capitalize()

        # Create the button list for the message
        button_list = [
            [{"text": "📺 Live Feeds", "callback_data": 'live_feed'}],
            [{"text": "📽️ Intruders Recording", "callback_data": 'recordings'}],
            [{"text": "📞 Emergency Contact", "callback_data": 'emergency'}],
        ]
        reply_markup = {"inline_keyboard": button_list}

        # Get all chat IDs from the subscription manager
        chat_ids = self.subscription.get_all_chat_ids()

        # Send a notification to all chat IDs
        for chat_id in chat_ids:
            self.send_message(
                chat_id, 
                f"🚨Alert! {status} Intruders Detected! \nView the live feeds here or access the recordings of the intruders:", 
                reply_markup=reply_markup
            )
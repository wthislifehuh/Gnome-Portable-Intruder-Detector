import asyncio
import requests
import aiohttp
import os
import json
from bleak import BleakScanner, BleakClient  # for Bluetooth scanning and connecting
from dotenv import load_dotenv
from database3 import SubscriptionManager
from collections import Counter

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
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        
        # Bluetooth configurations (for bleak)
        self.bluetooth_device_name = os.getenv('BLUETOOTH_DEVICE_NAME')
        self.phone_service_uuid = os.getenv('PHONE_SERVICE_UUID')
        self.phone_characteristic_uuid = os.getenv('PHONE_CHARACTERISTIC_UUID')
        
    async def human_trigger(self, result):
        if len(result) > 1:
            await self.send_notification(result)
        else:
            await self.send_notification("human")
        await self.trigger_alarm("human")

    async def animal_trigger(self, animal):
        if len(animal) > 1:
            await self.send_notification(animal)
            await self.trigger_alarm("human")
        else:
            animal_type = animal[0]
            await self.send_notification(animal_type)
            await self.trigger_alarm(animal_type)

    async def trigger_alarm(self, event):
        url = self.event_url_map.get(event)
        if url:
            async with aiohttp.ClientSession() as session:
                async with session.post(url) as response:
                    print(f'Triggered {event} event with status: {response.status}')
        else:
            print(f"Unknown event: {event}")

    async def send_message(self, chat_id: str, message: str, user_phone: str, reply_markup=None):
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
            return True
        else:
            print(f"Failed to send message to chat_id {chat_id}. Status code: {response.status_code}.")
            # Trigger SMS alert if Telegram message fails and phone number exists
            if user_phone:
                await self.send_bluetooth_sms(user_phone, message) # Send SMS via Bluetooth
            return False

    async def send_bluetooth_sms(self, phone_number: str, message: str):
        """
        Send an SMS via a Bluetooth connected phone using the provided phone number and message.
        This method will scan for nearby Bluetooth devices, find the phone, and send an SMS.
        """
        try:
            # Scan for Bluetooth devices
            devices = await BleakScanner.discover()
            target_device = None

            # Search for the specific Bluetooth phone by name
            for device in devices:
                if self.bluetooth_device_name in device.name:
                    target_device = device
                    break

            if not target_device:
                print(f"Bluetooth device {self.bluetooth_device_name} not found.")
                return

            # Connect to the phone via Bluetooth
            async with BleakClient(target_device.address) as client:
                print(f"Connected to {target_device.name}")

                # Send the SMS command (assuming the phone exposes a characteristic to send SMS)
                # This is an example, the actual command/characteristic UUIDs depend on the phone service
                sms_command = f"SendSMS:{phone_number}:{message}"
                await client.write_gatt_char(self.phone_characteristic_uuid, sms_command.encode('utf-8'))
                print(f"SMS sent via Bluetooth to {phone_number}")

        except Exception as e:
            print(f"Failed to send SMS via Bluetooth: {e}")

    async def send_notification(self, status):
        # Handle the animal or human status as before
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
            await self.send_message(
                chat_id,
                f"🚨Alert! {status} Intruders Detected! \nView the live feeds here or access the recordings of the intruders here.",
                user_phone=phone_number,
                reply_markup=reply_markup
            )

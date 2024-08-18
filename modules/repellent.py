# Using Method 3
import requests

class AlarmTrigger:
    def __init__(self):
        # Initialize the session object when the class is instantiated
        self.session = requests.Session()

    def pre_warm_connection(self):
        """
        Pre-warm the connection to reduce latency on the first request.
        This method can be called ahead of time to speed up subsequent requests.
        """
        self.session.get("https://app.vybit.net/trigger/pre-warm")

    def trigger_alarm(self, event):
        """
        Trigger an alarm based on the event type.
        Parameters:
            event (str): The type of event to trigger (e.g., 'human', 'dog', 'cat').
        """
        if event == "human":
            url = "https://app.vybit.net/trigger/cc6ghxxta9zkdcd5"
        elif event == "dog":
            url = "https://vybit.net/trigger/2uqg0zrx9wof9jgx"
        elif event == "cat":
            url = "https://app.vybit.net/trigger/cc6ghxxta9zkdcd5"
        else:
            print(f"Unknown event: {event}")
            return
        
        response = self.session.post(url)
        print(f'Triggered {event} event with status: {response.status_code}')


# Usage
alarm = AlarmTrigger()

# Pre-warm the connection (ideally do this in advance)
alarm.pre_warm_connection()

# Trigger the alarm
alarm.trigger_alarm("human")


# Method 1: 4sec to respond   ===============================================================
# If you need to handle multiple such events concurrently or in an environment where the blocking nature of synchronous requests is a concern

# import requests
# import asyncio
# import aiohttp

# async def trigger_alarm(event):
#     if event == "human":
#         async with aiohttp.ClientSession() as session:
#             async with session.post("https://app.vybit.net/trigger/cc6ghxxta9zkdcd5") as response:
#                 print(f'Triggered {event} event with status: {response.status}')

# asyncio.run(trigger_alarm("human"))



#  Method 2: 4 sec to respond ===============================================================
# Simplest way
# import requests

# # Create a session object
# session = requests.Session()
# def trigger_alarm(event):
#     if event == "human":
#         response = session.post("https://app.vybit.net/trigger/cc6ghxxta9zkdcd5")
#         print(f'Triggered {event} event with status: {response.status_code}')
# trigger_alarm("human")

# Method 3 - BEST PRE WARM THE SESSION ===================================
# provide the quickest response, as it minimizes the connection setup time
# import requests
# session = requests.Session()

# def pre_warm_connection():
#     # Pre-warm the connection to reduce latency on the first request
#     session.get("https://app.vybit.net/trigger/pre-warm")

# def trigger_alarm(event):
#     if event == "human":
#         # Use the pre-warmed session to make the POST request
#         response = session.post("https://app.vybit.net/trigger/cc6ghxxta9zkdcd5")
#         print(f'Triggered {event} event with status: {response.status_code}')
#     elif event == "dog":
#         response = session.post("https://vybit.net/trigger/2uqg0zrx9wof9jgx")
#         print(f'Triggered {event} event with status: {response.status_code}')
#     elif event == "cat":
#         response = session.post("https://app.vybit.net/trigger/cc6ghxxta9zkdcd5")
#         print(f'Triggered {event} event with status: {response.status_code}')

# # Usage
# pre_warm_connection() # use this in advance to warm up the connection first

# trigger_alarm("human")


# Combining Method 1 and Method 3 - 4 sec ===================================
# potentially provide even better performance, especially if you plan to make multiple HTTP requests concurrently

# import aiohttp
# import asyncio

# # Pre-warm the connection
# async def pre_warm_connection():
#     async with aiohttp.ClientSession() as session:
#         await session.get("https://app.vybit.net/trigger/pre-warm")

# # Trigger the alarm using async method
# async def trigger_alarm(event):
#     if event == "human":
#         async with aiohttp.ClientSession() as session:
#             async with session.post("https://app.vybit.net/trigger/cc6ghxxta9zkdcd5") as response:
#                 print(f'Triggered {event} event with status: {response.status}')

# async def main():
#     await pre_warm_connection()
#     await trigger_alarm("human")

# asyncio.run(main())




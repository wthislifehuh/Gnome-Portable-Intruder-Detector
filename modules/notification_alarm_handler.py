#noti_alarm_handler.py
import asyncio
from notifier import TelegramNotifier
from bot_handler import BotHandler
from database2 import SubscriptionManager
# , initialize_database
from alarm import AlarmTrigger


class NotificationAlarmHandler:
    def __init__(self):
        self.subscription = SubscriptionManager()
        self.alarm = AlarmTrigger()
        self.notifier = TelegramNotifier(self.subscription)

        
    async def human_trigger(self):
        self.notifier.send_notification("human")
        self.alarm.trigger_alarm("human")

    async def animal_trigger(self, detection_result):
        if len(detection_result['animal']) > 1:
            # Multiple animals, trigger common alarm, send notification for animals
            await self.notifier.send_notification(detection_result['animal'])  # Send notification for each animal
            self.alarm.trigger_alarm("human")  # Trigger common alarm for multiple animals
            
        else:
            # Single animal, trigger specific alarm
            animal_type = detection_result['animal'][0]
            await self.notifier.send_notification(animal_type)  # Send notification for the single animal
            self.alarm.trigger_alarm(animal_type)  # Trigger alarm specific to the animal

    # async def send_notification_and_trigger_alarm(self):
    #     if detection_result['is_intruder']:
    #         self.notifier.send_notification("human")
    #         self.alarm.trigger_alarm("human")
    #     elif detection_result['is_animal']:
    #         if len(detection_result['animal_array']) > 1:
    #             # Multiple animals, trigger human alarm
    #             self.notifier.send_notification("human")
    #             self.alarm.trigger_alarm("human")
    #         else:
    #             # Single animal, trigger specific alarm
    #             animal_type = detection_result['animal_array'][0]
    #             self.notifier.send_notification(animal_type)
    #             self.alarm.trigger_alarm(animal_type)
    #     else:
    #          print("Nothing to trigger")



# # example_bot_usage.py
# import asyncio
# from notifier import TelegramNotifier
# from bot_handler import BotHandler
# from database import initialize_database, SubscriptionManager

# async def external_trigger_monitor(notifier: TelegramNotifier):
#     while True:
#         await asyncio.sleep(10)  # Simulate checking for an external event every 5 seconds

#         # Example: simulate external event
#         is_event = True  # Replace with real event detection logic
#         if is_event:
#             print("Event Detected, sending notification...")
#             notifier.send_notification("human")

# async def main():
#     # Initialize the database and notifier
#     initialize_database()
#     subscription_manager = SubscriptionManager()
#     notifier = TelegramNotifier(subscription_manager)

#     # Initialize the bot handler
#     bot_handler = BotHandler(notifier)

#     # Run the bot and the trigger monitor concurrently
#     await asyncio.gather(
#         bot_handler.run(),
#         external_trigger_monitor(notifier)
#     )

# if __name__ == "__main__":
#     asyncio.run(main())
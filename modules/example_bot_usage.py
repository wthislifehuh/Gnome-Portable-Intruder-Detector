import asyncio
from notifier import TelegramNotifier
from bot_handler import BotHandler
from database import initialize_database, SubscriptionManager

async def external_trigger_monitor(notifier: TelegramNotifier):
    while True:
        await asyncio.sleep(100)  # Simulate checking for an external event every 5 seconds

        # Example: simulate external event
        is_event = True  # Replace with real event detection logic
        if is_event:
            print("Event Detected, sending notification...")
            notifier.send_notification("trigger")

async def main():
    # Initialize the database and notifier
    initialize_database()
    subscription_manager = SubscriptionManager()
    notifier = TelegramNotifier(subscription_manager)

    # Initialize the bot handler
    bot_handler = BotHandler(notifier)

    # Run the bot and the trigger monitor concurrently
    await asyncio.gather(
        bot_handler.run(),
        external_trigger_monitor(notifier)
    )

if __name__ == "__main__":
    asyncio.run(main())

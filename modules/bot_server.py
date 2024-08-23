# bot_run.py
import asyncio
from bot_handler import BotHandler
from notifier import TelegramNotifier
from database2 import  SubscriptionManager
# , initialize_database

async def main():
    # initialize_database()
    subscription_manager = SubscriptionManager()
    notifier = TelegramNotifier(subscription_manager)
    bot_handler = BotHandler(notifier)

    await bot_handler.run()

if __name__ == "__main__":
    asyncio.run(main())




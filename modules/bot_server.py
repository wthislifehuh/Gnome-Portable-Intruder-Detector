# bot_run.py
import asyncio
from bot_handler import BotHandler
from notification_alarm_handler import NotificationAlarmHandler
from database3 import  SubscriptionManager
# , initialize_database
  
async def main():
    # initialize_database()
    # subscription_manager = SubscriptionManager()
    bot_handler = BotHandler()

    await bot_handler.run()

if __name__ == "__main__":
    asyncio.run(main())





from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from notification_alarm_handler import NotificationAlarmHandler
from database3 import SubscriptionManager
import os
import re
from dotenv import load_dotenv
import asyncio

class BotHandler:
    def __init__(self):
        self.subscription_manager = SubscriptionManager()
        load_dotenv()
        self.token = os.getenv('BOT_TOKEN')
        self.application = Application.builder().token(self.token).build()
        self.livefeed_link = "http://192.168.1.5:5000"
        self.info_link = "https://playful-router-dca.notion.site/Gnome-Intruder-Detector-1ee22862e81244a8a083ee262e2274f8"
        

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        button_list = [
            [InlineKeyboardButton("📺 Live Stream", callback_data='live_feed')],
            [InlineKeyboardButton("📽️ Recordings", callback_data='recordings')],
            [InlineKeyboardButton("📌 Add Subscription Chat IDs", callback_data='subscription')],
            [InlineKeyboardButton("📍 Information", callback_data='info')],
            [InlineKeyboardButton("📞 Emergency", callback_data='emergency')],
        ]

        reply_markup = InlineKeyboardMarkup(button_list)

        await update.message.reply_text(
            "✨Thank you for using Gnome - Intruder Detector! \n\nIf you're new to our services, please subscribe to the channel of the intruder detector system and provide your chatID. Tap on the \"📌Subscription\" button to subscribe now! \n\nIf you want to know more, please visit our Info page. \n\nYou can control me by typing \"/\" and choose the services you want. ",
            reply_markup=reply_markup
        )

    async def button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        if query.data == 'subscription':
            await query.message.reply_text(f"Please enter your intruder detection channel subscription code and password.\nFormat: subscription_code<space>password\n\n📍NOTE: If you lost your subscription code, please contact our admin at @gnomeIntruderDetector. If you haven't sign up, please visit our website at {self.livefeed_link}")
            context.user_data['awaiting_subscription_code'] = True
        elif query.data == 'info':
            await query.message.reply_text(
                f"To know more about Gnome - Intruder detector, \nHere is the link to the bot information page: \n📍{self.info_link}. \n\nYou can also visit our website at \n📍{self.livefeed_link}.\n\nIf you have any questions, please contact us at \n@gnomeIntruderDetector.",
            )
        elif query.data == 'recordings':
            await self.list_recordings(update, context)
        elif query.data == 'live_feed':
            await self.get_livefeed(update, context)
        elif query.data == 'emergency':
            await query.message.reply_text(
                f"Here are some emergency contacts in Kampar: \n\n📞 General: 999\n📞 Bomba Kampar: 054664444\n📞 Hospital Kampar: 05465333\n📞 Police Kampar: 054652222"
            )
        else:
            await query.edit_message_text(text=f"Selected option: {query.data}")
        
    async def list_recordings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Determine the chat ID based on whether the function was triggered by a message or a callback query
        chat_id = None
        if update.message:
            chat_id = str(update.message.chat_id)
        elif update.callback_query:
            chat_id = str(update.callback_query.message.chat_id)
        
        if chat_id:
            # Check if the chat_id is subscribed to any channel
            subscription_code = self.subscription_manager.get_subscription_code_by_chat_id(chat_id)
            if subscription_code:
                # Construct the path to the subscription's video folder
                video_folder = os.path.join(os.path.dirname(__file__), f'../static/videos/{subscription_code}')
                
                if os.path.exists(video_folder):
                    video_files = os.listdir(video_folder)
                    if video_files:
                        numbered_list = "\n".join([f"{i+1}. {filename}" for i, filename in enumerate(video_files)])
                        response_text = f"📁 Available Recordings:\n{numbered_list}\n\nPlease send the number associated with the filename you want to view.\n\n🔗Note: The filename is the time of the intrusion in this format: [YYMMDDHHMMSS].webm"

                        if update.callback_query:
                            await update.callback_query.message.reply_text(response_text)
                        else:
                            await update.message.reply_text(response_text)

                        context.user_data['awaiting_filename'] = True
                        context.user_data['video_files'] = video_files
                        context.user_data['video_folder'] = video_folder  # Store the video folder in context
                    else:
                        if update.callback_query:
                            await update.callback_query.message.reply_text("🚫 No recordings found in the database.")
                        else:
                            await update.message.reply_text("🚫 No recordings found in the database.")
                else:
                    if update.callback_query:
                        await update.callback_query.message.reply_text(f"🚫 No recordings found for subscription code '{subscription_code}'.")
                    else:
                        await update.message.reply_text(f"🚫 No recordings found for subscription code '{subscription_code}'.")
            else:
                if update.callback_query:
                    await update.callback_query.message.reply_text("🚫 You are not authorized to access video recordings. Please subscribe first.")
                else:
                    await update.message.reply_text("🚫 You are not authorized to access video recordings. Please subscribe first.")
        else:
            if update.callback_query:
                await update.callback_query.message.reply_text("🚫 Unable to determine the chat ID. Please try again.")
            else:
                await update.message.reply_text("🚫 Unable to determine the chat ID. Please try again.")

    async def get_livefeed(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        response_text = f"Here is the link to the live feed: \n📍{self.livefeed_link}"
        if update.callback_query:
            await update.callback_query.message.reply_text(response_text)
        else:
            await update.message.reply_text(response_text)
        # Determine the chat ID based on whether the function was triggered by a message or a callback query
        # chat_id = None
        # if update.message:
        #     chat_id = str(update.message.chat_id)
        # elif update.callback_query:
        #     chat_id = str(update.callback_query.message.chat_id)
        
        # if chat_id:
        #     # Check if the chat_id is subscribed to any channel
        #     subscription_code = self.subscription_manager.get_subscription_code_by_chat_id(chat_id)
        #     if subscription_code:
        #         link = self.subscription_manager.get_livefeed(subscription_code)
        #         response_text = f"Here is the link to the live feed: \n📍{self.livefeed_link}"
        #         if update.callback_query:
        #             await update.callback_query.message.reply_text(response_text)
        #         else:
        #             await update.message.reply_text(response_text)
        #     else:
        #         reply_text = "🚫 You are not authorized to access livefeeds. Please subscribe first."
        #         if update.callback_query:
        #             await update.callback_query.message.reply_text(reply_text)
        #         else:
        #             await update.message.reply_text(reply_text)
        # else:
        #     reply_text = "🚫 You are not authorized to access livefeeds. Please subscribe first."
        #     if update.callback_query:
        #         await update.callback_query.message.reply_text(reply_text)
        #     else:
        #         await update.message.reply_text(reply_text)


        
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = str(update.message.chat_id)
        text = update.message.text
        context.user_data['subscription_code'] = text

        if context.user_data.get('awaiting_subscription_code'):
             # The pattern now captures a 6-digit subscription code and a password of at least 6 characters
            pattern = r'^(\d{6})\s+(\S{6,})$'
            match = re.match(pattern, text)
            if match:
                subscription_code = match.group(1)
                password = match.group(2)
                if len(subscription_code) == 6 and subscription_code.isdigit():
                    if self.subscription_manager.verify_subscription_code(subscription_code):
                        if self.subscription_manager.verify_password(subscription_code, password):
                            await update.message.reply_text("🎊 Subscription code verified. Please enter your chat_id. \n🔗NOTE: You can visit BOT @raw_info_bot and send any message to it to obtain your chat_id.")
                            context.user_data['awaiting_chat_id'] = True
                        else:
                            await update.message.reply_text(
                            "🚫 Wrong password! Sorry, you can't access our services without a correct password.Please sign up via our website - {self.live_feed}.",
                            reply_markup=InlineKeyboardMarkup([
                                [InlineKeyboardButton("📌Subscription", callback_data='subscription')],
                                [InlineKeyboardButton("📍Information", callback_data='info')]
                            ])
                            )
                    else:
                        await update.message.reply_text(
                        "🚫 Sorry, you can't access our services without a correct subscription code. Please sign up via our website - {self.live_feed}",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("📌Subscription", callback_data='subscription')],
                            [InlineKeyboardButton("📍Information", callback_data='info')]
                        ])
                        )
                else:
                    await update.message.reply_text(
                    "🚫 Sorry, you can't access our services without a correct subscription code format (6 digit).",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("📌Subscription", callback_data='subscription')],
                        [InlineKeyboardButton("📍Information", callback_data='info')]
                    ])
                    )
            else:
                await update.message.reply_text(
                    "🚫 Invalid input format. Please try again.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("📌Subscription", callback_data='subscription')],
                        [InlineKeyboardButton("📍Information", callback_data='info')]
                    ])
                    )
            context.user_data['awaiting_subscription_code'] = False

            
            # context.user_data['awaiting_subscription_code'] = False
            # if self.subscription_manager.verify_subscription_code(text):
            #     await update.message.reply_text("🎊 Subscription code verified. Please enter your chat_id. \n🔗NOTE: You can visit BOT @raw_info_bot and send any message to it to obtain your chat_id.")
            #     context.user_data['awaiting_chat_id'] = True
            # else:
            #     await update.message.reply_text(
            #         "🚫 Sorry, you can't access our services without a correct subscription code.",
            #         reply_markup=InlineKeyboardMarkup([
            #             [InlineKeyboardButton("📌Subscription", callback_data='subscription')],
            #             [InlineKeyboardButton("📍Information", callback_data='info')]
            #         ])
            #     )
        elif context.user_data.get('awaiting_chat_id'):
            if self.subscription_manager.verify_chat_id(context.user_data['subscription_code'], text):
                await update.message.reply_text("You are already subscribed and can access our services.")
            else:
                if len(text) == 10 and text.isdigit():
                    self.subscription_manager.add_chat_id(context.user_data['subscription_code'], text)
                    await update.message.reply_text("🎊 Chat ID added successfully! \nYou now have access to our services. 🚨 Notifications will be automatically sent to your account when intruders are detected.")
                else:
                    await update.message.reply_text("🚫 Invalid Chat ID format (10 digits) ! Please try again.")
            context.user_data['awaiting_chat_id'] = False
        elif context.user_data.get('awaiting_filename'):
            await self.handle_filename_selection(update, context, text)
        elif context.user_data.get('awaiting_admin_token'):
            if text == self.token:
                await self.admin_menu(update, context)
                context.user_data['awaiting_admin_token'] = False  
                context.user_data['awaiting_admin_action'] = True   
            else:
                await update.message.reply_text("🚫 Invalid token. Access denied.")
                context.user_data['awaiting_admin_token'] = False
        elif context.user_data.get('awaiting_admin_action'):
            await self.handle_admin_action(update, context, text)
        elif context.user_data.get('awaiting_new_subscription_code') or \
            context.user_data.get('awaiting_deletion_subscription_code') or \
            context.user_data.get('awaiting_deletion_chat_id') or \
            context.user_data.get('awaiting_update_livefeed'):
            await self.handle_admin_input(update, context, text)
        else:
            await self.start(update, context)

    def extract_datetime_info(self, filename):
        datetime_part = filename.split('.')[0]
        year = datetime_part[0:2]
        month = datetime_part[2:4]
        date = datetime_part[4:6]
        hour = datetime_part[6:8]
        minute = datetime_part[8:10]
        second = datetime_part[10:12]
        return f"Date: {date}/{month}/20{year}\nTime: {hour}:{minute}:{second}"

    async def handle_filename_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, selection: str):
        try:
            file_index = int(selection) - 1
            video_files = context.user_data.get('video_files', [])
            video_folder = context.user_data.get('video_folder', '')

            if 0 <= file_index < len(video_files):
                filename = video_files[file_index]
                video_path = os.path.join(video_folder, filename) 
                await update.message.reply_text(f"📹 Sending video: {filename}\n\n🚨 Intrusion time\n{self.extract_datetime_info(filename)}")
                await update.message.reply_video(video=open(video_path, 'rb'))
            else:
                await update.message.reply_text("🚫 Invalid selection. Please send the correct number associated with the filename.")
        except ValueError:
            await update.message.reply_text("🚫 Invalid input. Please send the number associated with the filename.")
        context.user_data['awaiting_filename'] = False

    async def admin_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "📋 Admin Menu:\n1. Add Subscription Code\n2. Delete Subscription Code\n3. Delete Chat ID\n4. View all chat IDs \n5. View all subscription codes\n6. Update livefeed link\n7. View all Subscriptions Info\n\nPlease select an action by typing the number."
        )
        context.user_data['awaiting_admin_action'] = True


    async def handle_admin_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE, action: str):
        if action == '1':
            await update.message.reply_text("Please enter the subscription code to add. \n\nFormat: subscription code<space>temporary password (more than 6 digits)")
            context.user_data['awaiting_new_subscription_code'] = True
            context.user_data['awaiting_admin_action'] = False
        elif action == '2':
            await update.message.reply_text("Please enter the subscription code to delete:")
            context.user_data['awaiting_deletion_subscription_code'] = True
            context.user_data['awaiting_admin_action'] = False
        elif action == '3':
            await update.message.reply_text("Please enter the chatID to delete. \n\nFormat: subscription code (6 digits) <space>chatID (10 digits):")
            context.user_data['awaiting_deletion_chat_id'] = True
            context.user_data['awaiting_admin_action'] = False
        elif action == '4':
            chatidlist = self.subscription_manager.get_all_chat_ids()
            if chatidlist:
                list = "\n".join([f"{i+1}. {chatid}" for i, chatid in enumerate(chatidlist)])
                await update.message.reply_text(f"📃 List of Chat IDs:\n\n{list}")
                await self.admin_menu(update, context)
            else:
                await update.message.reply_text("🚫 No chat IDs found. Returning to admin menu.")
                await self.admin_menu(update, context)
        elif action == '5':
            codelist = self.subscription_manager.get_all_subscription_ids()
            if codelist:
                list = "\n".join([f"{i+1}. {subscription_code}" for i, subscription_code in enumerate(codelist)])
                await update.message.reply_text(f"📃 List of Subscription Codes:\n\n{list}")
                await self.admin_menu(update, context)
            else:
                await update.message.reply_text("🚫 No Subscription Codes found. Returning to admin menu.")
                await self.admin_menu(update, context)
        elif action == '6':
            await update.message.reply_text("Please enter the subscription code and link to update. \n\nFollow this format: subscription_code <space> link")
            context.user_data['awaiting_update_livefeed'] = True
            context.user_data['awaiting_admin_action'] = False
        elif action == '7':
            infolist = self.subscription_manager.get_all()
            if infolist:
                await update.message.reply_text(f"📃 Subscriptions Info:\n\n{infolist}")
                await self.admin_menu(update, context)
            else:
                await update.message.reply_text("🚫 No info found. Returning to admin menu.")
                await self.admin_menu(update, context)
        else:
            await update.message.reply_text("🚫 Invalid selection. Returning to admin menu.")
            await self.admin_menu(update, context)

    async def handle_admin_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        if context.user_data.get('awaiting_new_subscription_code'):
            # The pattern now captures a 6-digit subscription code and a password of at least 6 characters
            pattern = r'^(\d{6})\s+(\S{6,})$'
            match = re.match(pattern, text)
            
            if match:
                subscription_code = match.group(1)
                password = match.group(2)
                
                if len(subscription_code) == 6 and subscription_code.isdigit():
                    if not self.subscription_manager.verify_subscription_code(subscription_code):
                        if len(password) >= 6:
                            self.subscription_manager.add_subscription(subscription_code, password)
                            await update.message.reply_text(f"Subscription code '{subscription_code}' added successfully!")
                            context.user_data['awaiting_admin_action'] = False
                        else:
                            await update.message.reply_text("🚫 Password needs to be more than 6 characters! Returning to admin menu.")
                            await self.admin_menu(update, context)
                    else:
                        await update.message.reply_text("🚫 Subscription code exists! Returning to admin menu.")
                        await self.admin_menu(update, context)
                else:
                    await update.message.reply_text("🚫 Invalid subscription code format (6 digits). Returning to admin menu.")
                    await self.admin_menu(update, context)
            else:
                await update.message.reply_text("🚫 Invalid input format. Returning to admin menu.")
                await self.admin_menu(update, context)
            
            context.user_data['awaiting_new_subscription_code'] = False

        elif context.user_data.get('awaiting_deletion_subscription_code'):
            if self.subscription_manager.verify_subscription_code(text):
                self.subscription_manager.delete_subscription(text)
                await update.message.reply_text(f"Subscription code '{text}' deleted successfully!")
                context.user_data['awaiting_admin_action'] = False
            else:
                await update.message.reply_text(f"🚫 Invalid subscription code. Returning to admin menu.")
                await self.admin_menu(update, context)
            context.user_data['awaiting_deletion_subscription_code'] = False
            
        elif context.user_data.get('awaiting_deletion_chat_id'):
            pattern = r'^(\d{6})\s+(\S{10})$'
            match = re.match(pattern, text)
            if match:
                subscription_code = match.group(1)
                chatId = match.group(2)
                if self.subscription_manager.verify_subscription_code(subscription_code):
                    if self.subscription_manager.verify_chat_id(subscription_code, chatId):
                        self.subscription_manager.delete_chat_id(subscription_code, chatId)
                        await update.message.reply_text(f"🎊 Chat ID '{chatId}' deleted successfully!")
                        await self.admin_menu(update, context)
                    else:
                        await update.message.reply_text(f"🚫 Invalid Chat ID. Returning to admin menu.")
                        await self.admin_menu(update, context)
                else:
                    await update.message.reply_text(f"🚫 Invalid Subscription code in '{text}'!")
                    await self.admin_menu(update, context)
            else:
                await update.message.reply_text(f"🚫 Invalid input format. Returning to admin menu.")
                await self.admin_menu(update, context)
            context.user_data['awaiting_deletion_chat_id'] = False

        elif context.user_data.get('awaiting_update_livefeed'):
            pattern = r'^(\d{6})\s+(https?://.+)'
            match = re.match(pattern, text)
            if match:
                subscription_code = match.group(1)
                url = match.group(2)
                if self.subscription_manager.verify_subscription_code(subscription_code):
                    self.subscription_manager.add_livefeed(subscription_code, url)
                    await update.message.reply_text(f"🎊 Livefeed URL '{url}' added in {subscription_code} successfully!")
                    context.user_data['awaiting_admin_action'] = False
                else:
                    await update.message.reply_text(f"🚫 Invalid Subscription code in '{text}'!")
                    await self.admin_menu(update, context)
            else:
                await update.message.reply_text(f"🚫 Invalid input format. Returning to admin menu.")
                await self.admin_menu(update, context)
            context.user_data['awaiting_update_livefeed'] = False

    async def livefeed(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = str(update.message.chat_id)
        if self.subscription_manager.verify_chat_id(context.user_data['subscription_code'], chat_id):
            await self.get_livefeed(update, context)
        else:
            await update.message.reply_text("🚫 You are not authorized to access the live feed. Please subscribe first.")
    
    async def info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(f"To know more about Gnome - Intruder detector, \nHere is the link to the information page: \n📍{self.info_link}\n\nYou can also visit our website at \n📍{self.livefeed_link}.\n\nIf you have any questions, please contact us at \n📍@gnomeIntruderDetector.")
    
    async def emergency(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(f"Here are some emergency contacts in Kampar: \n\n📞General: 999\n📞Bomba Kampar: 054664444\n📞Hospital Kampar: 05465333\n📞Police Kampar: 054652222")

    async def recordings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.list_recordings(update, context)

    async def prompt_subscription(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Please enter your intruder detection channel subscription code and password.\nFormat: subscription_code<space>password\n\n📍NOTE: If you lost your subscription code, please contact our admin at @gnomeIntruderDetector.")
        context.user_data['awaiting_subscription_code'] = True
    
    async def subscription(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.prompt_subscription(update, context)

    async def admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Please enter the bot token for verification:")
        context.user_data['awaiting_admin_token'] = True

    async def run(self):
        self.application.add_handler(CommandHandler('start', self.start))
        self.application.add_handler(CommandHandler('admin', self.admin))
        self.application.add_handler(CommandHandler('livefeed', self.livefeed))
        self.application.add_handler(CommandHandler('recordings', self.recordings))
        self.application.add_handler(CommandHandler('subscription', self.subscription))
        self.application.add_handler(CommandHandler('emergency', self.emergency))
        self.application.add_handler(CommandHandler('info', self.info))
        self.application.add_handler(CallbackQueryHandler(self.button)) 
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        print("Bot is running and waiting for user requests...")
        try:
            while True:
                await asyncio.sleep(5)
        except asyncio.CancelledError:
            print("Bot is shutting down...")
            await self.application.stop()
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from notifier import TelegramNotifier
from database import initialize_database, SubscriptionManager
import os
import asyncio

class BotHandler:
    def __init__(self, notifier: TelegramNotifier):
        self.notifier = notifier
        self.subscription_manager = notifier.subscription_manager
        self.application = Application.builder().token(notifier.token).build()
        # self.livefeed_link = "http://192.168.1.19:5000"
        self.subscription_code = None
        self.info_link = "https://playful-router-dca.notion.site/Gnome-Intruder-Detector-1ee22862e81244a8a083ee262e2274f8"
        

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        button_list = [
            [InlineKeyboardButton("📌 Subscription", callback_data='subscription')],
            [InlineKeyboardButton("📍 Information", callback_data='info')],
            [InlineKeyboardButton("📞 Emergency", callback_data='emergency')],
            [InlineKeyboardButton("📺 Live Stream", callback_data='live_feed')],
            [InlineKeyboardButton("📽️ Recordings", callback_data='recordings')]
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
            await query.message.reply_text("Please enter your intruder detection channel subscription code.\n\n📍NOTE: If you lost your subscription code, please contact our admin at @gnomeIntruderDetector.")
            context.user_data['awaiting_subscription_code'] = True
        elif query.data == 'info':
            await query.message.reply_text(
                f"To know more about Gnome - Intruder detector, \nHere is the link to the information page: \n📍{self.info_link}",
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
                        response_text = f"📁 Available Recordings:\n{numbered_list}\n\nPlease send the number associated with the filename you want to view."

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
                link = self.subscription_manager.get_livefeed(subscription_code)
                response_text = f"Here is the link to the live feed: \n📍{link}",
                if update.callback_query:
                    await update.callback_query.message.reply_text(response_text)
                else:
                    await update.message.reply_text(response_text)

        
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = str(update.message.chat_id)
        text = update.message.text

        if context.user_data.get('awaiting_subscription_code'):
            context.user_data['subscription_code'] = text
            context.user_data['awaiting_subscription_code'] = False

            if self.subscription_manager.verify_subscription_code(text):
                await update.message.reply_text("🎊 Subscription code verified. Please enter your chat_id. \nNOTE: You can visit BOT @raw_info_bot and send any message to it to obtain your chat_id.")
                context.user_data['awaiting_chat_id'] = True
            else:
                await update.message.reply_text(
                    "🚫 Sorry, you can't access our services without a correct subscription code.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("📌Subscription", callback_data='subscription')],
                        [InlineKeyboardButton("📍Information", callback_data='info')]
                    ])
                )
        elif context.user_data.get('awaiting_chat_id'):
            if self.subscription_manager.verify_chat_id(text):
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
            if text == self.notifier.token:
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
            context.user_data.get('awaiting_deletion_chat_id') or\
            context.user_data.get('awaiting_add_livefeed'):
            await self.handle_admin_input(update, context, text)
        else:
            await self.start(update, context)

    # async def handle_filename_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, selection: str):
    #     try:
    #         file_index = int(selection) - 1
    #         video_files = context.user_data.get('video_files', [])
    #         if 0 <= file_index < len(video_files):
    #             filename = video_files[file_index]
    #             video_path = os.path.join(self.video_folder, filename)
    #             await update.message.reply_text(f"📹 Sending video: {filename}")
    #             await update.message.reply_video(video=open(video_path, 'rb'))
    #         else:
    #             await update.message.reply_text("🚫 Invalid selection. Please send the correct number associated with the filename.")
    #     except ValueError:
    #         await update.message.reply_text("🚫 Invalid input. Please send the number associated with the filename.")
    #     context.user_data['awaiting_filename'] = False
    async def handle_filename_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, selection: str):
        try:
            file_index = int(selection) - 1
            video_files = context.user_data.get('video_files', [])
            video_folder = context.user_data.get('video_folder', '')

            if 0 <= file_index < len(video_files):
                filename = video_files[file_index]
                video_path = os.path.join(video_folder, filename)  # Use the correct video folder
                await update.message.reply_text(f"📹 Sending video: {filename}")
                await update.message.reply_video(video=open(video_path, 'rb'))
            else:
                await update.message.reply_text("🚫 Invalid selection. Please send the correct number associated with the filename.")
        except ValueError:
            await update.message.reply_text("🚫 Invalid input. Please send the number associated with the filename.")
        context.user_data['awaiting_filename'] = False

    # ============================ Admin =====================================
    async def admin_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "📋 Admin Menu:\n1. Add Subscription Code\n2. Delete Subscription Code\n3. Delete Chat ID\n4. View all chat IDs\n5. View all subscription codes \n6. Add Live Feed\n\nPlease select an action by typing the number."
        )
        context.user_data['awaiting_admin_action'] = True


    async def handle_admin_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE, action: str):
        if action == '1':
            await update.message.reply_text("Please enter the subscription code to add:")
            context.user_data['awaiting_new_subscription_code'] = True
            context.user_data['awaiting_admin_action'] = False
        elif action == '2':
            await update.message.reply_text("Please enter the subscription code to delete:")
            context.user_data['awaiting_deletion_subscription_code'] = True
            context.user_data['awaiting_admin_action'] = False
        elif action == '3':
            await update.message.reply_text("Please enter the chat ID to delete:")
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
        if action == '6':
            await update.message.reply_text("Please enter the livefeed subscription code to add the livefeed:")
            context.user_data['awaiting_add_livefeed'] = True
            context.user_data['awaiting_admin_action'] = False
        else:
            await update.message.reply_text("🚫 Invalid selection. Returning to admin menu.")
            await self.admin_menu(update, context)

    async def handle_admin_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        if context.user_data.get('awaiting_new_subscription_code'):
            if len(text) == 6 and text.isdigit():
                self.subscription_manager.add_subscription(text)
                await update.message.reply_text(f"Subscription code '{text}' added successfully!")
                context.user_data['awaiting_admin_action'] = False
            else:
                await update.message.reply_text(f"🚫 Invalid subscription code format (6 digits). Returning to admin menu.")
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
            if self.subscription_manager.verify_chat_id(text):
                self.subscription_manager.delete_chat_id(text)
                await update.message.reply_text(f"Chat ID '{text}' deleted successfully!")
                context.user_data['awaiting_admin_action'] = False
            else:
                await update.message.reply_text(f"🚫 Invalid Chat ID. Returning to admin menu.")
                await self.admin_menu(update, context)
            context.user_data['awaiting_deletion_chat_id'] = False
        elif context.user_data.get('awaiting_add_livefeed'):
            context.user_data['awaiting_add_livefeed'] = False
            if self.subscription_manager.verify_subscription_code(text):
                await update.message.reply_text("🎊 Subscription code verified. \nPlease enter the live feed link to add.")
                # await self.add_livefeed(update, context, text)
                self.subscription = text
                context.user_data['awaiting_new_livefeed'] = True
            else:
                await update.message.reply_text("🚫 Sorry, invalid subscription code.")
        elif context.user_data.get('awaiting_new_livefeed'):
            text = update.message.text
            if self.subscription_manager.add_livefeed(self.subscription_code, text):
                await update.message.reply_text("Live feed link added successfully.")
                await self.admin_menu(update, context)
                context.user_data['awaiting_new_livefeed'] = False

            
    # async def add_livefeed(self, update: Update, context: ContextTypes.DEFAULT_TYPE, subscription_code:str):
    #     context.user_data['awaiting_new_livefeed'] = True
    #     if context.user_data.get('awaiting_new_livefeed'):
    #         text = update.message.text
    #         if self.subscription_manager.add_livefeed(self.subscription_code, text):
    #             await update.message.reply_text("Live feed link added successfully.")
    #             await self.admin_menu(update, context)
    #             context.user_data['awaiting_new_livefeed'] = False

    async def livefeed(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = str(update.message.chat_id)
        if self.subscription_manager.verify_chat_id(chat_id):
            await self.get_livefeed(update, context)
        else:
            await update.message.reply_text("🚫 You are not authorized to access the live feed. Please subscribe first.")
    
    async def info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(f"To know more about Gnome - Intruder detector, \nHere is the link to the information page: \n📍{self.info_link}")
    
    async def emergency(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(f"Here are some emergency contacts in Kampar: \n\n📞General: 999\n📞Bomba Kampar: 054664444\n📞Hospital Kampar: 05465333\n📞Police Kampar: 054652222")

    async def recordings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.list_recordings(update, context)

    async def prompt_subscription(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Please enter your intruder detection channel subscription code.\n\n📍NOTE: If you lost your subscription code, please contact our admin at @gnomeIntruderDetector.")
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
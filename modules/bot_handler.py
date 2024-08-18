from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from notifier import TelegramNotifier
from database import initialize_database, SubscriptionManager

class BotHandler:
    def __init__(self, notifier: TelegramNotifier):
        self.notifier = notifier
        self.subscription_manager = notifier.subscription_manager
        self.application = Application.builder().token(notifier.token).build()
        self.livefeed_link = "http://192.168.1.19:5000"
        self.info_link = "https://playful-router-dca.notion.site/Gnome-Intruder-Detector-1ee22862e81244a8a083ee262e2274f8"
        

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        button_list = [
            [InlineKeyboardButton("Subscription", callback_data='subscription')],
            [InlineKeyboardButton("Information", callback_data='info')]
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
            await query.message.reply_text("Please enter your subscription code:")
            context.user_data['awaiting_subscription_code'] = True
        elif query.data == 'info':
            await query.message.reply_text(
                f"To know more about Gnome - Intruder detector, \nHere is the link to the information page: \n📍{self.info_link}",
            )
        elif query.data == 'send_video':
            # Send the video file to the user
            video_path = os.path.join(os.path.dirname(__file__), '../static/videos/030326.mp4')
            await query.message.reply_video(video=open(video_path, 'rb'))
            #TODO: replace time with systme recording time
            await query.message.reply_text(
                f"👆🏻 Here is the latest video recording of the intruders at TIME",
            )
        elif query.data == 'live_feed':
            # Reply with the live feed link
            await query.message.reply_text(
                f"Here is the link to the live feed: \n📍{self.livefeed_link}",
            )
        else:
            await query.edit_message_text(text=f"Selected option: {query.data}")
        

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = str(update.message.chat_id)
        text = update.message.text

        if context.user_data.get('awaiting_subscription_code'):
            context.user_data['subscription_code'] = text
            context.user_data['awaiting_subscription_code'] = False

            if self.subscription_manager.verify_subscription_code(text):
                await update.message.reply_text("🎊 Subscription code verified. Please enter your chat_id. \nNOTE: You can visit BOT 'RawDataBot' and send any message to it to obtain your chat_id.")
                context.user_data['awaiting_chat_id'] = True
            else:
                await update.message.reply_text(
                    "🚫 Sorry, you can't access our services without a correct subscription code.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("Subscription", callback_data='subscription')],
                        [InlineKeyboardButton("Information", callback_data='info')]
                    ])
                )
        elif context.user_data.get('awaiting_chat_id'):
            if self.subscription_manager.verify_chat_id(text):
                await update.message.reply_text("You are already subscribed and can access our services.")
            else:
                self.subscription_manager.add_chat_id(context.user_data['subscription_code'], text)
                await update.message.reply_text("🎊 Chat ID added successfully! \nYou now have access to our services. 🚨 Notifications will be automatically sent to your account when intruders are detected.")
            context.user_data['awaiting_chat_id'] = False
        elif context.user_data.get('awaiting_admin_token'):
            if text == self.notifier.token:
                await update.message.reply_text("Token verified. Please enter the new subscription code:")
                context.user_data['awaiting_admin_token'] = False
                context.user_data['awaiting_new_subscription_code'] = True
            else:
                await update.message.reply_text("🚫 Invalid token. Access denied.")
                context.user_data['awaiting_admin_token'] = False
        elif context.user_data.get('awaiting_new_subscription_code'):
            self.subscription_manager.add_subscription(text)
            await update.message.reply_text(f"Subscription code '{text}' added successfully!")
            context.user_data['awaiting_new_subscription_code'] = False

    async def livefeed(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = str(update.message.chat_id)
        if self.subscription_manager.verify_chat_id(chat_id):
            await update.message.reply_text(f"Here is the link to the live feed: \n📍{self.livefeed_link}")
        else:
            await update.message.reply_text("🚫 You are not authorized to access the live feed. Please subscribe first.")
    
    async def info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(f"To know more about Gnome - Intruder detector, \nHere is the link to the information page: \n📍{self.info_link}",)
    
    async def prompt_subscription(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Prompt the user to enter their subscription code."""
        await update.message.reply_text("Please enter your subscription code:")
        context.user_data['awaiting_subscription_code'] = True
    
    async def subscription(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /subscription command."""
        await self.prompt_subscription(update, context)

    async def admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Please enter the bot token for verification:")
        context.user_data['awaiting_admin_token'] = True

    async def run(self):
        self.application.add_handler(CommandHandler('start', self.start))
        self.application.add_handler(CommandHandler('admin', self.admin))
        self.application.add_handler(CommandHandler('livefeed', self.livefeed))
        self.application.add_handler(CommandHandler('subscription', self.subscription))
        self.application.add_handler(CommandHandler('info', self.info))
        self.application.add_handler(CallbackQueryHandler(self.button))  # Ensure this is correct
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        await self.application.initialize()  # Ensure the application is initialized
        await self.application.start()  # Start the application
        await self.application.updater.start_polling()  # Start polling

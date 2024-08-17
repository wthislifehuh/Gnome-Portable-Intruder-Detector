# from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
# from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
# import os

# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     # Creating buttons
#     button_list = [
#         [InlineKeyboardButton("Live Feeds", callback_data='live_feed')],
#         [InlineKeyboardButton("Intruders Recording", callback_data='send_video')]
#     ]

#     # Creating the markup
#     reply_markup = InlineKeyboardMarkup(button_list)

#     # Sending the message with buttons
#     await update.message.reply_text(
#         "✨Thank you for using Gnome - Intruder Detector! \nYou can type \"\\\" to view the command that you can enter. Or\n you can choose the services we provide here:",
#         reply_markup=reply_markup
#     )

# async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     livefeedLink = "http://192.168.1.19:5000"
#     query = update.callback_query
#     await query.answer()

#     # Check which button was pressed
#     if query.data == 'send_video':
#         # Send the video file to the user
#         video_path = os.path.join(os.path.dirname(__file__), '../static/videos/intruders.mp4')
#         await query.message.reply_video(video=open(video_path, 'rb'))
#     elif query.data == 'live_feed':
#         # Reply with the live feed link
#         await query.message.reply_text(
#             f"Here is the link to the live feed: \n📍{livefeedLink}",
#         )
#     else:
#         # Update the message text based on the button pressed
#         await query.edit_message_text(text=f"Selected option: {query.data}")

# def main():
#     application = Application.builder().token("7333024088:AAHgT9nWtrz7En_2hIii0Bc_RHkb6NZmT4I").build()
#     application.add_handler(CommandHandler('start', start))
#     application.add_handler(CallbackQueryHandler(button))
#     application.run_polling()

# if __name__ == '__main__':
#     main()





from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import os

# The allowed chat ID for accessing the video and live feed
ALLOWED_CHAT_ID = "1116943112"

# Dictionary to store chat IDs of users
user_chat_ids = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    await update.message.reply_text(
        f"Please enter your chat ID to proceed:"
    )
    user_chat_ids[chat_id] = None  # Store the user's chat ID in a dictionary

async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    user_input = update.message.text.strip()

    # Store the user-provided chat ID
    user_chat_ids[chat_id] = user_input

    if user_input == ALLOWED_CHAT_ID:
        # Provide options to the user
        button_list = [
            [InlineKeyboardButton("Live Feeds", callback_data='live_feed')],
            [InlineKeyboardButton("Intruders Recording", callback_data='send_video')]
        ]
        reply_markup = InlineKeyboardMarkup(button_list)
        await update.message.reply_text(
            "✨Thank you for using Gnome - Intruder Detector! \nYou can type \"\\\" to view the command that you can enter. Or\n you can choose the services we provide here:",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            "Invalid chat_id. \nYou have not registered as a Gnome user. Please register it via /registerChat"
        )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.callback_query.message.chat_id

    # Check if the user's chat ID is allowed
    if user_chat_ids.get(chat_id) == ALLOWED_CHAT_ID:
        livefeedLink = "http://192.168.1.19:5000"
        query = update.callback_query
        await query.answer()

        # Check which button was pressed
        if query.data == 'send_video':
            # Send the video file to the user
            video_path = os.path.join(os.path.dirname(__file__), '../static/videos/intruders.mp4')
            await query.message.reply_video(video=open(video_path, 'rb'))
        elif query.data == 'live_feed':
            # Reply with the live feed link
            await query.message.reply_text(
                f"Here is the link to the live feed: \n📍{livefeedLink}",
            )
        else:
            # Update the message text based on the button pressed
            await query.edit_message_text(text=f"Selected option: {query.data}")
    else:
        await update.callback_query.message.reply_text(
            "Invalid chat_id. You have not registered a Gnome account. Please register it via /registerChat"
        )

def main():
    application = Application.builder().token("7333024088:AAHgT9nWtrz7En_2hIii0Bc_RHkb6NZmT4I").build()

    # Handlers for different commands and messages
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_chat_id))

    application.run_polling()

if __name__ == '__main__':
    main()

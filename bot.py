import os
import logging
from pytube import YouTube
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from flask import Flask
import asyncio
import re
import aiofiles
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_TOKEN = os.getenv('TELEGRAM_API_TOKEN', '7679008149:AAFPfEGh7HdlCg5_PGUWMhVf-nj6zXqBDzA')  # Replace with your actual token or keep it as is for testing

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# Constants for conversation steps
CHOOSING_RESOLUTION, DOWNLOADING = range(2)

# Telegram bot handlers
async def start(update, context):
    await update.message.reply_text("Hello! Send me a YouTube link, and I'll give you a download option.")

async def handle_youtube_link(update, context):
    try:
        youtube_url = update.message.text
        match = re.search(r'(https?://[^\s]+)', youtube_url)
        if match:
            youtube_url = match.group(0)
        else:
            await update.message.reply_text("Please send a valid YouTube link.")
            return

        if "youtube.com" not in youtube_url and "youtu.be" not in youtube_url:
            await update.message.reply_text("Please send a valid YouTube link.")
            return
        
        await update.message.reply_text("Processing your YouTube link...")
        yt = YouTube(youtube_url)

        streams = yt.streams.filter(progressive=True)
        available_resolutions = {stream.resolution: stream for stream in streams}

        if not available_resolutions:
            await update.message.reply_text("No downloadable streams found.")
            return

        keyboard = [[InlineKeyboardButton(res, callback_data=res) for res in available_resolutions.keys()]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("Choose a resolution:", reply_markup=reply_markup)
        context.user_data['available_resolutions'] = available_resolutions
        return CHOOSING_RESOLUTION

    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        await update.message.reply_text(f"Error processing video: {str(e)}")

async def choose_resolution(update, context):
    query = update.callback_query
    await query.answer()
    selected_resolution = query.data
    available_resolutions = context.user_data['available_resolutions']
    
    # Check if the selected resolution exists
    if selected_resolution not in available_resolutions:
        await query.message.reply_text("Selected resolution is not available. Please choose again.")
        return

    selected_stream = available_resolutions[selected_resolution]
    video_title = selected_stream.title.replace(" ", "_")
    video_path = f"{video_title}_{selected_resolution}.mp4"
    
    try:
        await query.message.reply_text(f"Downloading video in {selected_resolution}...")
        selected_stream.download(filename=video_path)

        # Send the video to the user
        await query.message.reply_video(video=open(video_path, 'rb'), caption=f"Here is your video: {video_title}")
    except Exception as e:
        logger.error(f"Error downloading video: {str(e)}")
        await query.message.reply_text(f"Error downloading video: {str(e)}")
    finally:
        # Clean up the downloaded file
        if os.path.exists(video_path):
            os.remove(video_path)

# Run the Telegram bot asynchronously
async def run_telegram_bot():
    application = Application.builder().token(API_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_youtube_link))
    application.add_handler(CallbackQueryHandler(choose_resolution))  # Corrected filter to CallbackQueryHandler

    # Start polling
    await application.start_polling()
    await application.idle()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 6000))

    # Run Flask server in the main thread
    flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port))
    flask_thread.start()

    # Run Telegram bot asynchronously
    asyncio.run(run_telegram_bot())

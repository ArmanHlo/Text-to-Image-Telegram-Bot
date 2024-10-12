import os
from pytube import YouTube
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from flask import Flask
import threading
import re

# Use environment variables for sensitive information
API_TOKEN = os.getenv('TELEGRAM_API_TOKEN', '7679008149:AAFPfEGh7HdlCg5_PGUWMhVf-nj6zXqBDzA')

# Flask app for port binding
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# Constants for conversation steps
CHOOSING_RESOLUTION, DOWNLOADING = range(2)

# Handle the start command
async def start(update, context):
    '''Start command handler'''
    await update.message.reply_text("Hello! Send me a YouTube link, and I'll give you a download option for the video.")

# Handle YouTube links
async def handle_youtube_link(update, context):
    '''Process YouTube link and give download options'''
    try:
        # Get YouTube URL from the user's message
        youtube_url = update.message.text

        # Check if it's a valid YouTube URL and clean it
        match = re.search(r'(https?://[^\s]+)', youtube_url)  # Extract the main URL
        if match:
            youtube_url = match.group(0)  # Use the cleaned URL
        else:
            await update.message.reply_text("Please send a valid YouTube link.")
            return

        if "youtube.com" not in youtube_url and "youtu.be" not in youtube_url:
            await update.message.reply_text("Please send a valid YouTube link.")
            return
        
        await update.message.reply_text("Processing your YouTube link...")

        # Download the YouTube video using pytube
        yt = YouTube(youtube_url)

        # Get all available streams
        streams = yt.streams.filter(progressive=True)  # Filter for video with audio
        available_resolutions = {stream.resolution: stream for stream in streams}

        if not available_resolutions:
            await update.message.reply_text("No downloadable streams found.")
            return

        # Create a list of resolution buttons
        keyboard = [[InlineKeyboardButton(res, callback_data=res) for res in available_resolutions.keys()]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("Choose a resolution:", reply_markup=reply_markup)

        # Set the conversation state
        context.user_data['available_resolutions'] = available_resolutions
        return CHOOSING_RESOLUTION

    except Exception as e:
        await update.message.reply_text(f"Error processing video: {str(e)}")

# Handle user selection of resolution
async def choose_resolution(update, context):
    query = update.callback_query
    await query.answer()

    selected_resolution = query.data
    available_resolutions = context.user_data['available_resolutions']
    selected_stream = available_resolutions[selected_resolution]

    video_title = selected_stream.title.replace(" ", "_")
    video_path = f"{video_title}_{selected_resolution}.mp4"
    
    try:
        await query.message.reply_text(f"Downloading video in {selected_resolution}...")

        # Download the video to local file
        selected_stream.download(filename=video_path)

        # Send the video file to the user
        await query.message.reply_video(video=open(video_path, 'rb'), caption=f"Here is your video: {video_title}")

    except Exception as e:
        await query.message.reply_text(f"Error downloading video: {str(e)}")

    finally:
        # Clean up the file after sending it
        if os.path.exists(video_path):
            os.remove(video_path)

# Run the Telegram bot
def run_telegram_bot():
    # Set up the application with the bot token
    application = Application.builder().token(API_TOKEN).build()

    # Command and message handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_youtube_link))
    application.add_handler(MessageHandler(filters.CallbackQuery, choose_resolution))

    # Start polling for updates
    application.run_polling()

if __name__ == '__main__':
    # Start the Flask server in a separate thread
    port = int(os.environ.get('PORT', 5000))  # Use port from environment variable or default to 5000
    threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': port}).start()

    # Run the Telegram bot
    run_telegram_bot()

import os
from pytube import YouTube
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from flask import Flask
import threading

# Use environment variables for sensitive information
API_TOKEN = os.getenv('TELEGRAM_API_TOKEN', '7679008149:AAFPfEGh7HdlCg5_PGUWMhVf-nj6zXqBDzA')

# Flask app for port binding
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

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

        # Check if it's a valid YouTube URL
        if "youtube.com" not in youtube_url and "youtu.be" not in youtube_url:
            await update.message.reply_text("Please send a valid YouTube link.")
            return
        
        await update.message.reply_text("Processing your YouTube link...")

        # Download the YouTube video using pytube
        yt = YouTube(youtube_url)

        # Get the highest resolution stream for download
        stream = yt.streams.get_highest_resolution()

        # Specify file path for download (use the video's title)
        video_title = yt.title.replace(" ", "_")
        video_path = f"{video_title}.mp4"
        
        # Download the video to local file
        stream.download(filename=video_path)

        # Send the video file back to the user
        await update.message.reply_text(f"Downloading video: {yt.title}")
        
        # Send the video file to the user
        await update.message.reply_video(video=open(video_path, 'rb'))
        
        # Clean up the file after sending it
        if os.path.exists(video_path):
            os.remove(video_path)

    except Exception as e:
        await update.message.reply_text(f"Error processing video: {str(e)}")

# Run the Telegram bot
def run_telegram_bot():
    # Set up the application with the bot token
    application = Application.builder().token(API_TOKEN).build()

    # Command and message handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_youtube_link))

    # Start polling for updates
    application.run_polling()

if __name__ == '__main__':
    # Start the Flask server in a separate thread
    port = int(os.environ.get('PORT', 6000))  # Use port from environment variable or default to 5000
    threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': port}).start()

    # Run the Telegram bot
    run_telegram_bot()

import os
import telebot
import pytube
from flask import Flask
import threading

app = Flask(__name__)

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
bot = telebot.TeleBot('7679008149:AAFPfEGh7HdlCg5_PGUWMhVf-nj6zXqBDzA')

# Route for checking if Flask app is running
@app.route('/')
def home():
    return "Flask app is running and Telegram bot is operational."

# Telegram bot handler for YouTube links
@bot.message_handler(func=lambda message: message.text.startswith('https://www.youtube.com/'))
def download_youtube_video(message):
    try:
        # Extract video ID from the YouTube URL
        video_url = message.text
        yt = pytube.YouTube(video_url)

        # Create a temporary directory to store the downloaded video
        temp_dir = os.path.join(os.getcwd(), 'temp')
        os.makedirs(temp_dir, exist_ok=True)

        # Download the video in the highest resolution available
        stream = yt.streams.get_highest_resolution()
        video_path = os.path.join(temp_dir, f'{yt.video_id}.mp4')
        stream.download(filename=video_path)

        # Send the downloaded video to the user
        with open(video_path, 'rb') as video_file:
            bot.send_document(message.chat.id, video_file, caption='Here is your downloaded YouTube video')

        # Remove the temporary video file
        os.remove(video_path)

    except Exception as e:
        # Handle potential errors and send an appropriate message to the user
        bot.send_message(message.chat.id, f"Error downloading video: {str(e)}")

# Function to run the Telegram bot
def run_telegram_bot():
    bot.polling()

# Start the Flask app and Telegram bot concurrently
if __name__ == '__main__':
    # Run Flask in a separate thread
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=6000)).start()

    # Run Telegram bot
    run_telegram_bot()

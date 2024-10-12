import os
import telebot
import pytube
from youtube_dl import YoutubeDL

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
bot = telebot.TeleBot('7679008149:AAFPfEGh7HdlCg5_PGUWMhVf-nj6zXqBDzA')

@bot.message_handler(func=lambda message: message.text.startswith('https://www.youtube.com/'))
def download_youtube_video(message):
    try:
        # Extract the YouTube video ID from the shared link
        video_id = message.text.split('=')[1]

        # Create a temporary directory to store the downloaded video
        temp_dir = os.path.join(os.getcwd(), 'temp')
        os.makedirs(temp_dir, exist_ok=True)

        # Use pytube to download the video in the highest resolution available
        yt = pytube.YouTube(f'https://www.youtube.com/watch?v={video_id}')
        stream = yt.streams.get_highest_resolution()

        # Download the video to the temporary directory
        video_path = os.path.join(temp_dir, f'{video_id}.mp4')
        stream.download(filename=video_path)

        # Send the downloaded video to the user
        with open(video_path, 'rb') as video_file:
            bot.send_document(message.chat.id, video_file, caption='Here is your downloaded YouTube video')

        # Remove the temporary video file
        os.remove(video_path)

    except Exception as e:
        # Handle potential errors and send an appropriate message to the user
        bot.send_message(message.chat.id, f"Error downloading video: {str(e)}")

# Start the Telegram bot
bot.polling()

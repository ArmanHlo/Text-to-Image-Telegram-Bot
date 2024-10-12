import os
import requests
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from io import BytesIO
from PIL import Image
from telegram import Update
from flask import Flask
import threading
from apscheduler.schedulers.background import BackgroundScheduler

# Use environment variables for sensitive information
TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN', 'cXrwQwz9h3rzVzCkwT5mdIrbJY6LzSxw5JlNz4KGEyCaCkH6WPJe7ybI')
UNSPLASH_API_KEY = os.getenv('UNSPLASH_API_KEY', 'aNzTrVHwB-aL3x5KW5FpNubfRLFw5nVr3512Jxde0KQ')
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY', 'cXrwQwz9h3rzVzCkwT5mdIrbJY6LzSxw5JlNz4KGEyCaCkH6WPJe7ybI')

# Flask app for port binding
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# Keep-alive ping function
def ping_self():
    url = "https://your-render-url.com"  # Replace with your Render app's URL
    try:
        requests.get(url)
        print(f"Pinged {url} to keep the app alive.")
    except Exception as e:
        print(f"Failed to ping the app: {e}")

# Fetch image from Unsplash
def fetch_image_unsplash(query):
    url = f"https://api.unsplash.com/photos/random?query={query}&client_id={UNSPLASH_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        image_url = response.json()["urls"]["regular"]
        return image_url
    else:
        raise Exception("Error fetching image from Unsplash: " + response.text)

# Fetch image from Pexels
def fetch_image_pexels(query):
    url = f"https://api.pexels.com/v1/search?query={query}&per_page=1"
    headers = {'Authorization': PEXELS_API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200 and response.json()['photos']:
        image_url = response.json()['photos'][0]['src']['original']
        return image_url
    else:
        raise Exception("Error fetching image from Pexels: " + response.text)

# Handle the user's prompt and fetch the image
async def handle_prompt(update: Update, context):
    user_input = update.message.text
    await update.message.reply_text("Fetching an image based on your prompt...")

    try:
        # Fetch image from Unsplash
        unsplash_image_url = fetch_image_unsplash(user_input)
        
        # Fetch image from Pexels
        pexels_image_url = fetch_image_pexels(user_input)

        # Send images back to the user
        await context.bot.send_photo(chat_id=update.message.chat.id, photo=unsplash_image_url, caption="From Unsplash")
        await context.bot.send_photo(chat_id=update.message.chat.id, photo=pexels_image_url, caption="From Pexels")
    
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

# Start command handler
async def start(update, context):
    await update.message.reply_text("Hello! Send me a prompt, and I will fetch an image for you!")

# Run the Telegram bot
def run_telegram_bot():
    application = Application.builder().token(TELEGRAM_API_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_prompt))

    application.run_polling()

if __name__ == '__main__':
    # Start the Flask server in a separate thread
    port = int(os.environ.get('PORT', 6000))  # Port for Flask
    threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': port}).start()

    # Run the Telegram bot
    run_telegram_bot()

    # Set up the scheduler to ping the app URL every 5 minutes
    scheduler = BackgroundScheduler()
    scheduler.add_job(ping_self, 'interval', minutes=1)
    scheduler.start()

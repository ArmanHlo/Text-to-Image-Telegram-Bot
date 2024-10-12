import os
import requests
import numpy as np
from PIL import Image
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from io import BytesIO
from flask import Flask
import threading
from apscheduler.schedulers.background import BackgroundScheduler

# Flask app to keep the bot alive
flask_app = Flask(__name__)

# Set your API keys directly in the code
PEXELS_API_KEY = "cXrwQwz9h3rzVzCkwT5mdIrbJY6LzSxw5JlNz4KGEyCaCkH6WPJe7ybI"  # Replace with your Pexels API key
UNSPLASH_ACCESS_KEY = "aNzTrVHwB-aL3x5KW5FpNubfRLFw5nVr3512Jxde0KQ"  # Replace with your Unsplash Access Key
TELEGRAM_BOT_TOKEN = "7679008149:AAFPfEGh7HdlCg5_PGUWMhVf-nj6zXqBDzA"  # Replace with your Telegram Bot token


# Function to search images using Pexels API
def search_image(description):
    headers = {
        "Authorization": PEXELS_API_KEY
    }
    url = f"https://api.pexels.com/v1/search?query={description}&per_page=1"
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data["photos"]:
            return data["photos"][0]["src"]["original"]
    return None

# Function to search images using Unsplash API
def search_unsplash_image(description):
    url = f"https://api.unsplash.com/photos/random?query={description}&client_id={UNSPLASH_ACCESS_KEY}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["urls"]["regular"]
    return None

# Start command to welcome users
async def start(update, context):
    await update.message.reply_text("Hello! Send me a description, and I'll fetch an image for you.")

# Handle user input for image generation
async def handle_message(update, context):
    description = update.message.text
    await update.message.reply_text(f"Searching for an image based on: {description}...")

    # Search for an image (you can switch between Pexels or Unsplash here)
    image_url = search_image(description)  # Pexels
    # image_url = search_unsplash_image(description)  # Unsplash

    if image_url:
        # Fetch and convert the image to JPG
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        img_jpg = img.convert('RGB')

        # Save and send the JPG image
        img_jpg.save('image.jpg')
        with open('image.jpg', 'rb') as img_file:
            await update.message.reply_photo(photo=img_file)
    else:
        await update.message.reply_text("Sorry, I couldn't find an image for that description.")

# Main function to run the bot
async def run_telegram_bot():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command and message handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot
    await app.start()
    await app.idle()

# Flask endpoint to run the bot
@flask_app.route("/")
def home():
    return "Telegram Bot is running."

# Function to run the Flask server
def run_flask():
    port = int(os.getenv('PORT', 6000))  # Use port 6000 for Flask
    flask_app.run(host='0.0.0.0', port=port)

# Scheduler to keep the bot alive (optional)
def keep_alive():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=run_flask, trigger="interval", seconds=300)  # Example job to ping Flask every hour
    scheduler.start()

if __name__ == "__main__":
    import asyncio

    # Start the Flask server in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Run the Telegram bot on the main thread
    asyncio.run(run_telegram_bot())

    # Start the background scheduler
    keep_alive()

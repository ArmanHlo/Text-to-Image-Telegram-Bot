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
TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN', '7679008149:AAFPfEGh7HdlCg5_PGUWMhVf-nj6zXqBDzA')
# DEEPAI_API_KEY = os.getenv('DEEPAI_API_KEY', 'YOUR_DEEPAI_API_KEY')  # Remove if you are no longer using DeepAI

# Flask app for port binding
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# Keep-alive ping function
def ping_self():
    url = "https://text-to-image-telegram-bot.onrender.com"  # Replace with your Render app's URL
    try:
        requests.get(url)
        print(f"Pinged {url} to keep the app alive.")
    except Exception as e:
        print(f"Failed to ping the app: {e}")

# Fetch image from Craiyon
async def fetch_image_craiyon(prompt):
    url = "https://api.craiyon.com/generate"  # Craiyon API endpoint
    data = {"prompt": prompt}

    response = requests.post(url, json=data)

    if response.status_code == 200:
        # Craiyon returns a list of image URLs
        image_urls = response.json().get('images', [])
        if image_urls:
            return image_urls[0]  # Return the first image URL
        else:
            raise Exception("No images found.")
    else:
        raise Exception("Error fetching image from Craiyon: " + response.text)

# Download image from URL and save as JPG
def download_image_as_jpg(image_url, output_path):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    img = img.convert("RGB")  # Convert to RGB for JPG
    img.save(output_path, "JPEG")

# Handle the user's prompt and fetch the image
async def handle_prompt(update: Update, context):
    user_input = update.message.text
    await update.message.reply_text("Generating an image based on your prompt...")

    try:
        # Fetch image from Craiyon
        craiyon_image_url = await fetch_image_craiyon(user_input)

        # Save the image as JPG and send it to the user
        output_path = f"image_{update.message.from_user.id}.jpg"
        download_image_as_jpg(craiyon_image_url, output_path)

        with open(output_path, 'rb') as img_file:
            await context.bot.send_photo(chat_id=update.message.chat.id, photo=img_file)

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

# Start command handler
async def start(update, context):
    await update.message.reply_text("Hello! Send me a prompt, and I will generate an image in JPG format for you!")

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

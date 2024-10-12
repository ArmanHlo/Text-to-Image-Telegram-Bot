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
IMG_GEN_API_KEY = os.getenv('IMG_GEN_API_KEY', '7fbfb5d9-7d41-4fc6-b295-9c00d5c01b38')  # Add your ImgGen AI API key here


# Flask app for port binding
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# Keep-alive ping function
def ping_self():
    url = "https://your-render-app-url.onrender.com"  # Replace with your Render app's URL
    try:
        requests.get(url)
        print(f"Pinged {url} to keep the app alive.")
    except Exception as e:
        print(f"Failed to ping the app: {e}")

# Fetch image from ImgGen AI
async def fetch_image_imggen(prompt):
    url = "https://api.imggen.ai/v1/generate"  # Use the correct ImgGen API URL, adjust if needed
    headers = {
        'Authorization': f'Bearer {IMG_GEN_API_KEY}', 
        'Content-Type': 'application/json'
    }
    data = {
        'prompt': prompt,
        'n': 1  # Requesting one image, check documentation for additional options
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        # Adjust the key based on the API response format
        return response.json().get('data')[0].get('url')  # Hypothetical structure, change as needed
    else:
        raise Exception("Error fetching image from ImgGen AI: " + response.text)

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
        # Fetch image from ImgGen AI
        imggen_image_url = await fetch_image_imggen(user_input)

        # Save the image as JPG and send it to the user
        output_path = f"image_{update.message.from_user.id}.jpg"
        download_image_as_jpg(imggen_image_url, output_path)

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

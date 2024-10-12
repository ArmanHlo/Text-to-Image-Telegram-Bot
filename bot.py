import os
import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from PIL import Image
from io import BytesIO
from flask import Flask

# Flask app to keep the bot alive and listen on port 6000
app = Flask(__name__)

# Set your API keys for Pexels or Unsplash directly in the code
PEXELS_API_KEY = "cXrwQwz9h3rzVzCkwT5mdIrbJY6LzSxw5JlNz4KGEyCaCkH6WPJe7ybI"  # Replace with your Pexels API key
UNSPLASH_ACCESS_KEY = "aNzTrVHwB-aL3x5KW5FpNubfRLFw5nVr3512Jxde0KQ"  # Replace with your Unsplash Access Key
TELEGRAM_BOT_TOKEN = "7679008149:AAFPfEGh7HdlCg5_PGUWMhVf-nj6zXqBDzA"  # Replace with your Telegram Bot token

# Function to search images using Pexels API
async def search_image(description):
    headers = {
        "Authorization": PEXELS_API_KEY
    }
    url = f"https://api.pexels.com/v1/search?query={description}&per_page=1"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data["photos"]:
                return data["photos"][0]["src"]["original"]
        return None

# Function to search images using Unsplash API
async def search_unsplash_image(description):
    url = f"https://api.unsplash.com/photos/random?query={description}&client_id={UNSPLASH_ACCESS_KEY}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            return data["urls"]["regular"]
        return None

# Start command to welcome users
async def start(update: Update, context):
    await update.message.reply_text("Hello! Send me a description, and I'll fetch an image for you.")

# Handle user input for image generation
async def handle_message(update: Update, context):
    description = update.message.text
    await update.message.reply_text(f"Searching for an image based on: {description}...")

    # Search for an image (you can switch between Pexels or Unsplash here)
    image_url = await search_image(description)  # Pexels
    # image_url = await search_unsplash_image(description)  # Unsplash

    if image_url:
        # Fetch and convert the image to JPG
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url)
            img = Image.open(BytesIO(response.content))
            img_jpg = img.convert('RGB')

            # Save and send the JPG image
            img_jpg.save('image.jpg')
            with open('image.jpg', 'rb') as img_file:
                await update.message.reply_photo(photo=img_file)
    else:
        await update.message.reply_text("Sorry, I couldn't find an image for that description.")

# Main function to run the bot
async def run_bot():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command and message handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot
    await app.start()
    await app.idle()

# Flask endpoint to run the bot on port 6000
@app.route("/")
def home():
    return "Telegram Bot is running."

if __name__ == "__main__":
    import asyncio

    # Run the bot using asyncio
    asyncio.run(run_bot())

    # Run the Flask app on port 6000
    app.run(host="0.0.0.0", port=6000)

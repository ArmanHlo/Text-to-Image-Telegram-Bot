import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from io import BytesIO
from PIL import Image
from flask import Flask
import threading
import socket
import logging
import asyncio

# Set up logging for troubleshooting
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Set your API keys directly
TELEGRAM_BOT_TOKEN = "7679008149:AAFPfEGh7HdlCg5_PGUWMhVf-nj6zXqBDzA"  # Replace with your Telegram Bot token

# Function to check if a port is available
def is_port_available(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

# Start command to welcome users
async def start(update: Update, context):
    logger.info(f"Received /start command from {update.message.from_user.first_name}")
    await update.message.reply_text("Hello! Welcome to the bot. Send me a description, and I'll fetch an image for you.")

# Handle user input for image generation
async def handle_message(update: Update, context):
    description = update.message.text
    logger.info(f"Received message: {description}")

    await update.message.reply_text(f"Searching for an image based on: {description}...")

    # Placeholder for image search, can be integrated later
    await update.message.reply_text("Sorry, the image search functionality is not yet available.")

# Function to start the Telegram bot
async def run_telegram_bot():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command handler for /start
    app.add_handler(CommandHandler("start", start))
    # Add message handler for text input
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.initialize()
    logger.info("Telegram bot is starting...")
    await app.start()
    await app.idle()

# Flask route
@app.route('/')
def index():
    return "Flask server is running!"

if __name__ == '__main__':
    # Define port for Flask
    port = 10001  # Change port to avoid conflicts

    # Check if the port is available
    if not is_port_available(port):
        logger.error(f"Port {port} is already in use. Please free it up before running the server.")
    else:
        # Start the Flask server in a separate thread
        threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': port}).start()

        # Start the Telegram bot
        asyncio.run(run_telegram_bot())

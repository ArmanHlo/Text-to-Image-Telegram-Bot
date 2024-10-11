import os
import logging
import threading
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "Telegram Bot and Flask Server are running!"

# Define a simple function for keyword-based responses
def get_response(text):
    responses = {
        "hello": "Hello! How can I assist you today?",
        "how are you": "I'm just a bot, but I'm doing great! How about you?",
        "what is your name": "I'm your friendly Telegram bot!",
        "bye": "Goodbye! Have a great day!",
    }
    for keyword, response in responses.items():
        if keyword in text.lower():
            return response
    return "I'm not sure how to respond to that."

# Start command for the bot
async def start(update: Update, context):
    await update.message.reply_text('Welcome! Ask me anything!')

# Handle incoming text messages
async def handle_message(update: Update, context):
    try:
        text = update.message.text
        answer = get_response(text)
        await update.message.reply_text(answer)
    except Exception as e:
        logger.error(f"Error in handle_message: {e}")

# Function to run the Telegram bot
async def run_telegram_bot():
    application = ApplicationBuilder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await application.run_polling()

if __name__ == '__main__':
    # Start the Telegram bot in a separate asyncio event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Run the Telegram bot in a separate thread
    telegram_thread = threading.Thread(target=loop.run_until_complete, args=(run_telegram_bot(),))
    telegram_thread.start()
    
    # Run the Flask app
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)  # Start Flask app

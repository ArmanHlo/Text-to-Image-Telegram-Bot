import os
import logging
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
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
    text = update.message.text
    answer = get_response(text)
    await update.message.reply_text(answer)

# Function to run the Telegram bot
def run_telegram_bot():
    application = ApplicationBuilder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)  # Start Flask app
    run_telegram_bot()  # Start Telegram bot

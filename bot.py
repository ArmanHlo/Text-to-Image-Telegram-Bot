import os
import logging
import requests
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
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
    return "Telegram AI Bot is running!"

# Function to generate a response using Hugging Face Transformers API
def generate_response(prompt):
    # Hugging Face Inference API endpoint for a text generation model
    hf_api_url = "https://api-inference.huggingface.co/models/distilgpt2"  # You can change the model here
    headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}
    
    response = requests.post(hf_api_url, headers=headers, json={"inputs": prompt})
    if response.status_code == 200:
        return response.json()[0]['generated_text']
    else:
        logger.error(f"Error generating response: {response.text}")
        return "Sorry, I couldn't process your request."

# Start command for the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Welcome! You can ask me anything.')

# Handle incoming text messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    answer = generate_response(user_message)
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

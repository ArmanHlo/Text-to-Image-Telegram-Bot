import os
import threading
import logging
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
from transformers import pipeline  # Import Hugging Face's pipeline

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

# Start command for the bot
async def start(update: Update, context):
    await update.message.reply_text('Welcome! Send me a description and I will create an image out of it or ask me any question!')

# Function to generate an image from a text description using OpenAI
def generate_image_from_text(description):
    try:
        response = openai.Image.create(
            prompt=description,
            n=1,  # Generate one image
            size="512x512"  # Image size
        )
        image_url = response['data'][0]['url']  # Get the image URL from the response
        return image_url
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        return None

# Function to get answers to questions using OpenAI
def get_answer_from_openai(question):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Choose the appropriate model
            messages=[{"role": "user", "content": question}]
        )
        answer = response.choices[0].message['content']
        return answer
    except Exception as e:
        logger.error(f"Error getting answer: {e}")
        return "Sorry, I couldn't process your question."

# Hugging Face text generation pipeline
hugging_face_pipeline = pipeline("text-generation", model="gpt2")

# Function to get answers from Hugging Face
def get_answer_from_huggingface(question):
    try:
        # Generate text using Hugging Face's GPT-2
        result = hugging_face_pipeline(question, max_length=100, num_return_sequences=1)
        return result[0]['generated_text']
    except Exception as e:
        logger.error(f"Error generating text with Hugging Face: {e}")
        return "Sorry, I couldn't process your question."

# Handle incoming text messages
async def handle_message(update: Update, context):
    text = update.message.text

    # Check if the text is a description for an image or a question
    if "image" in text.lower():  # Simple check for image requests
        description = text.replace("image", "").strip()
        image_url = generate_image_from_text(description)

        if image_url:
            await update.message.reply_photo(photo=image_url)
        else:
            await update.message.reply_text('Sorry, I couldn\'t generate an image from that description.')
    else:
        # If OpenAI API key is available, use OpenAI, otherwise use Hugging Face
        if os.getenv('OPENAI_API_KEY'):
            answer = get_answer_from_openai(text)
        else:
            answer = get_answer_from_huggingface(text)
        
        await update.message.reply_text(answer)

# Function to run the Telegram bot
def run_telegram_bot():
    # Build the Telegram bot application with the token from environment variables
    application = ApplicationBuilder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()

    # Add command and message handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    # Start the Flask server in a separate thread
    port = int(os.environ.get('PORT', 5000))  # Port for Flask
    threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': port}).start()

    # Run the Telegram bot
    run_telegram_bot()

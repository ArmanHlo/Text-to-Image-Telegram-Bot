from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler

# Define a function to handle the /start command
async def start(update: Update, context):
    user_first_name = update.message.from_user.first_name
    await update.message.reply_text(f"Hello, {user_first_name}! Welcome to the Telegram bot.")

# Main function to run the bot
if __name__ == '__main__':
    # Replace 'YOUR_BOT_TOKEN' with the token you got from BotFather
    bot_token = '7679008149:AAFPfEGh7HdlCg5_PGUWMhVf-nj6zXqBDzA'
    
    # Initialize the bot
    app = ApplicationBuilder().token(bot_token).build()
    
    # Add a handler for the /start command
    app.add_handler(CommandHandler("start", start))
    
    # Start the bot
    print("Bot is running...")
    app.run_polling()

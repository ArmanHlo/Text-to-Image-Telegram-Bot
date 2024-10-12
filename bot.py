import telebot
from diffusers import StableDiffusionPipeline
import torch
from flask import Flask, request, abort

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
bot = telebot.TeleBot('7679008149:AAFPfEGh7HdlCg5_PGUWMhVf-nj6zXqBDzA')

# Load the Stable Diffusion model
model_id = "runwayml/stable-diffusion-v1-5"  # Replace with your preferred model

# Ensure that the pipeline runs on the appropriate device (CPU/GPU)
device = "cuda" if torch.cuda.is_available() else "cpu"
pipe = StableDiffusionPipeline.from_pretrained(model_id)
pipe = pipe.to(device)  # Move the pipeline to the appropriate device

# Flask app to run webhook on port 6000
app = Flask(__name__)

# Your bot's URL (this needs to be publicly accessible)
WEBHOOK_URL = 'https://yourdomain.com/webhook'

@app.route("/webhook", methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    else:
        abort(403)

@bot.message_handler(func=lambda message: True)
def generate_image(message):
    prompt = message.text
    try:
        # Generate image using the provided prompt
        image = pipe(prompt, guidance_scale=7.5, num_inference_steps=20).images[0]
        image_path = "output.jpg"
        image.save(image_path)
        
        # Send the image back to the user
        with open(image_path, "rb") as img:
            bot.send_photo(message.chat.id, img)
    
    except Exception as e:
        bot.send_message(message.chat.id, f"Error generating image: {str(e)}")

if __name__ == "__main__":
    # Set up the webhook
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)

    # Run Flask app on port 6000
    app.run(host='0.0.0.0', port=6000)

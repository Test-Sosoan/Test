import os
import telebot
from flask import Flask, request

API_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, "Hi there, I am EchoBot")

# Webhook route for Render
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        return 'Invalid content type', 403

if __name__ == '__main__':
    # Set webhook on Render
    bot.remove_webhook()
    bot.set_webhook(url=f"https://your-render-app-name.onrender.com/webhook")
    app.run(host='0.0.0.0', port=10000)

# main.py
import os
import telebot
from flask import Flask, request
import threading
import time
import asyncio
import re
from url import check_url

API_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# Simple user registration system
registered_users = set()

def is_registered(user_id):
    return user_id in registered_users

# UptimeRobot အတွက် root endpoint
@app.route('/')
def home():
    return "Bot is running!", 200

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, "Hi there, I am EchoBot")

@bot.message_handler(commands=['register'])
def register_user(message):
    user_id = message.from_user.id
    registered_users.add(user_id)
    bot.reply_to(message, "You are now registered.")

# URL checking command
@bot.message_handler(commands=['url'])
def send_url(message):
    user_id = message.from_user.id
    if not is_registered(user_id):
        bot.reply_to(message, "You must register first by sending `/register`.")
        return

    url = message.text[len('/url '):].strip()
    if not re.match(r'^https?://[^\s]+$', url):
        bot.reply_to(message, "Invalid URL format.")
        return

    bot0 = bot.reply_to(message, "Please wait... ⏳")
    
    # Run async function in a separate thread
    def run_async():
        try:
            result = asyncio.run(check_url(url))
            bot.edit_message_text(result, chat_id=bot0.chat.id, message_id=bot0.message_id)
        except Exception as e:
            bot.edit_message_text(f"Error: {e}", chat_id=bot0.chat.id, message_id=bot0.message_id)
    
    thread = threading.Thread(target=run_async)
    thread.start()

# Webhook route for Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        return 'Invalid content type', 403

# Keep-alive function for UptimeRobot
def keep_alive():
    while True:
        # Ping own URL every 10 minutes to prevent sleep
        try:
            import requests
            requests.get("https://your-bot-name.onrender.com")
        except:
            pass
        time.sleep(600)  # 10 minutes

if __name__ == '__main__':
    # Start keep-alive thread
    thread = threading.Thread(target=keep_alive)
    thread.daemon = True
    thread.start()
    
    # Set webhook
    bot.remove_webhook()
    bot.set_webhook(url="https://your-bot-name.onrender.com/webhook")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=10000)

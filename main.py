# main.py
import os
import telebot
from flask import Flask, request
import threading
import time
import asyncio
import re
from url import check_url
from s1 import stripe_1d
from database import get_user_role, is_user_registered, add_user

API_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# Rate limiting system
user_last_command = {}

def is_rate_limited(user_id):
    current_time = time.time()
    if user_id in user_last_command:
        if current_time - user_last_command[user_id] < 5:  # 5 seconds cooldown
            return True
    user_last_command[user_id] = current_time
    return False

def has_permission(user_id, permission_type):
    user_role = get_user_role(user_id)
    
    if permission_type == "owner":
        return user_role == "owner"
    elif permission_type == "premium":
        return user_role in ["premium", "owner"]
    return False

# UptimeRobot အတွက် root endpoint
@app.route('/')
def home():
    return "Bot is running!", 200

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    user_id = message.from_user.id
    if not is_user_registered(user_id):
        add_user(user_id, 'user')  # Auto-register new users as regular users
    
    # Create help message based on user role
    help_text = "👋 Welcome to EchoBot!\n\nAvailable commands:\n"
    help_text += "/help - Show this help message\n"
    help_text += "/id - Show your user ID and role\n"
    help_text += "/register - Register as a user\n"
    help_text += "/url <url> - Check a URL\n"
    
    # Add premium commands if user has premium access
    if has_permission(user_id, "premium"):
        help_text += "/chk <card_details> - Check card details (Premium only)\n"
    
    # Add admin commands if user is owner
    if has_permission(user_id, "owner"):
        help_text += "/promote <user_id> <role> - Promote a user (Owner only)\n"
    
    bot.reply_to(message, help_text)

# Add this new command handler for /id
@bot.message_handler(commands=['id'])
def show_user_id(message):
    user_id = message.from_user.id
    if not is_user_registered(user_id):
        add_user(user_id, 'user')
    
    user_role = get_user_role(user_id)
    bot.reply_to(message, f"👤 Your User ID: {user_id}\n🎭 Your Role: {user_role}")

@bot.message_handler(commands=['register'])
def register_user(message):
    user_id = message.from_user.id
    if not is_user_registered(user_id):
        add_user(user_id, 'user')
        bot.reply_to(message, "You are now registered as a regular user.")
    else:
        bot.reply_to(message, "You are already registered.")

# Admin command to promote users
@bot.message_handler(commands=['promote'])
def promote_user(message):
    user_id = message.from_user.id
    if not has_permission(user_id, "owner"):
        bot.reply_to(message, "You don't have permission to use this command.")
        return
    
    try:
        # Extract target user ID from command
        target_user_id = int(message.text.split()[1])
        new_role = message.text.split()[2].lower()
        
        if new_role not in ['user', 'premium', 'owner']:
            bot.reply_to(message, "Invalid role. Use: user, premium, or owner")
            return
            
        add_user(target_user_id, new_role)
        bot.reply_to(message, f"User {target_user_id} has been promoted to {new_role}.")
    except (IndexError, ValueError):
        bot.reply_to(message, "Usage: /promote <user_id> <role>")

# URL checking command
@bot.message_handler(commands=['url'])
def send_url(message):
    user_id = message.from_user.id
    if not is_user_registered(user_id):
        bot.reply_to(message, "You must register first by sending `/register`.")
        return

    url = message.text[len('/url '):].strip()
    if not re.match(r'^https?://[^\s]+$', url):
        bot.reply_to(message, "Invalid URL format.")
        return

    bot0 = bot.reply_to(message, "Please wait... ⏳")
    
    def run_async():
        try:
            result = asyncio.run(check_url(url))
            bot.edit_message_text(result, chat_id=bot0.chat.id, message_id=bot0.message_id)
        except Exception as e:
            bot.edit_message_text(f"Error: {e}", chat_id=bot0.chat.id, message_id=bot0.message_id)
    
    thread = threading.Thread(target=run_async)
    thread.start()

# Stripe checking command
@bot.message_handler(commands=['chk'])
def send_stripe(message):
    user_id = message.from_user.id
    if not has_permission(user_id, "premium"):
        bot.reply_to(message, "You do not have permission to use this command. Only Premium or Owner roles can access this feature.")
        return
    
    if is_rate_limited(user_id):
        bot.reply_to(message, "You are sending messages too fast. Please slow down.")
        return
    
    bot0 = bot.reply_to(message, "Checking your card...")
    card_details = message.text[len('/chk '):].strip()
    
    if card_details:
        def run_async_stripe():
            try:
                result = asyncio.run(stripe_1d(card_details))
                bot.edit_message_text(result, chat_id=bot0.chat.id, message_id=bot0.message_id)
            except Exception as e:
                bot.edit_message_text(f"Error: {e}", chat_id=bot0.chat.id, message_id=bot0.message_id)
        
        thread = threading.Thread(target=run_async_stripe)
        thread.start()
    else:
        bot.edit_message_text("Usage: /chk {card_details}", chat_id=bot0.chat.id, message_id=bot0.message_id)

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
        try:
            import requests
            requests.get("https://your-bot-name.onrender.com")
        except:
            pass
        time.sleep(600)

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

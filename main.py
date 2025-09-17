import os
import telebot

API_TOKEN = os.getenv('API_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, """\
Hi there, I am EchoBot
""")

if __name__ == '__main__':
    print("I am working!")
    bot.infinity_polling()

import os
import random
import telebot
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

jokes = [
    "Почему программисты путают Хэллоуин и Рождество? Потому что Oct 31 == Dec 25 😄",
    "Баг — это не ошибка, это недокументированная фича 🐛",
    "Работает? Не трогай! 🙏",
    "Сколько программистов нужно, чтобы вкрутить лампочку? Ни одного, это аппаратная проблема 💡",
]


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привет! 👋 Я бот-шутник. Напиши /help, чтобы узнать, что я умею."
    )


@bot.message_handler(commands=["help"])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "Вот что я умею:\n"
        "/start - поздороваться 👋\n"
        "/help - список команд 📋\n"
        "/joke - рассказать шутку 😂"
    )


@bot.message_handler(commands=["joke"])
def joke(message):
    bot.send_message(message.chat.id, random.choice(jokes))


@bot.message_handler(func=lambda message: True)
def other(message):
    bot.send_message(message.chat.id, "Я такое не понимаю 🤔 Попробуй /help")


print("Бот запущен...")
bot.polling()


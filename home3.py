# import os
# import logging
# import random
# from pathlib import Path


# import telebot
# from dotenv import load_dotenv

# telebot.logger.setLevel(logging.DEBUG)

# env_path = Path(__file__).parent / ".env"
# load_dotenv(env_path, override=True)


# TOKEN = os.getenv("BOT_TOKEN")

# if not TOKEN:
#     raise SystemExit("Токен не найден: Проверь .env")

# bot = telebot.TeleBot(TOKEN)

# JOKES = [
#     "Почему программисты путают Хэллоуин и Рождество? Потому что Oct 31 == Dec 25 🎃",
#     "— Сколько программистов нужно, чтобы вкрутить лампочку? — Ни одного, это аппаратная проблема 💡",
#     "Баг — это не ошибка, а недокументированная фича 🐛",
#     "Python — единственный змей, которого я не боюсь 🐍",
# ]

# FACTS = [
#     "Язык Python назван в честь комик-группы Monty Python, а не в честь змеи 🐍",
#     "Первый компьютерный баг был настоящим мотыльком, найденным в реле компьютера 🦋",
#     "Первое сообщение по ARPANET (прообраз интернета) было «LO» — система упала на «LOGIN» 🌐",
# ]


# @bot.message_handler(commands=["start"])
# def start(message):
#     name = message.from_user.first_name
#     bot.send_message(
#         message.chat.id,
#         f"Привет, {name}! 👋 Я бот-шутник.\nНапиши /help, чтобы увидеть, что я умею.",
#     )


# @bot.message_handler(commands=["help"])
# def help_command(message):
#     bot.send_message(
#         message.chat.id,
#         "Вот что я умею:\n"
#         "/start — поздороваться 👋\n"
#         "/help — список команд 📋\n"
#         "/joke — случайная шутка 😂\n"
#         "/dice — бросить кубик 🎲\n"
#         "/fact — интересный факт 🧠\n\n"
#         "А ещё можешь просто написать мне что-нибудь!",
#     )


# @bot.message_handler(commands=["joke"])
# def joke(message):
#     bot.send_message(message.chat.id, random.choice(JOKES))


# @bot.message_handler(commands=["dice"])
# def dice(message):
#     number = random.randint(1, 6)
#     bot.send_message(message.chat.id, f"Тебе выпало: {number} 🎲")


# @bot.message_handler(commands=["fact"])
# def fact(message):
#     bot.send_message(message.chat.id, random.choice(FACTS))


# @bot.message_handler(content_types=["text"])
# def reply_to_text(message):
#     text = message.text.lower()

#     if "привет" in text:
#         answer = "И тебе привет! 😄"
#     elif "как дела" in text:
#         answer = "Отлично, я же бот — у меня нет проблем, только баги 🐛"
#     elif "пока" in text:
#         answer = "До встречи! 👋"
#     else:
#         answer = f"Ты написал: «{message.text}». Попробуй /joke 😉"

#     bot.send_message(message.chat.id, answer)


# print("Бот запущен...")
# bot.infinity_polling()
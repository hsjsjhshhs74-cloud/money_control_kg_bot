import os
import sqlite3
from dotenv import load_dotenv
import telebot


load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)


def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS User (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            first_name TEXT,
            last_name TEXT,
            age INTEGER,
            city TEXT,
            street TEXT,
            phone TEXT
        )
    """)
    conn.commit()
    conn.close()


@bot.message_handler(commands=["start"])
def start_command(message):
    tg_id = message.from_user.id
    first_name = message.from_user.first_name or "Не указано"
    last_name = message.from_user.last_name or "Не указано"

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM User WHERE telegram_id = ?", (tg_id,))
    user = cursor.fetchone()

    if user is None:
        cursor.execute(
            """
            INSERT INTO User (telegram_id, first_name, last_name, age, city, street, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (tg_id, first_name, last_name, 0, "Не указан", "Не указана", "Не указан"),
        )
        conn.commit()
        bot.send_message(
            message.chat.id,
            f"Привет, {first_name}! Я успешно сохранил тебя в базу данных.",
        )
    else:
        bot.send_message(
            message.chat.id,
            f"С возвращением, {first_name}! Ты уже есть в моей базе.",
        )

    conn.close()

@bot.message_handler(commands=["me"])
def me_command(message):
    tg_id = message.from_user.id

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM User WHERE telegram_id = ?", (tg_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        text = (
            f"📋 **Твоя анкета:**\n"
            f"Имя: {user[2]}\n"
            f"Фамилия: {user[3]}\n"
            f"Возраст: {user[4]}\n"
            f"Город: {user[5]}\n"
            f"Улица: {user[6]}\n"
            f"Телефон: {user[7]}"
        )
        bot.send_message(message.chat.id, text, parse_mode="Markdown")
    else:
        bot.send_message(
            message.chat.id, "Тебя ещё нет в базе. Нажми /start для регистрации."
        )


@bot.message_handler(commands=["users"])
def users_command(message):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, first_name, last_name, city FROM User")
    all_users = cursor.fetchall()
    conn.close()

    if not all_users:
        bot.send_message(message.chat.id, "База данных пока пуста.")
        return

    text = "👥 **Список всех пользователей:**\n\n"
    for u in all_users:
        text += f"{u[0]}. {u[1]} {u[2]} (Город: {u[3]})\n"

    bot.send_message(message.chat.id, text, parse_mode="Markdown")


if __name__ == "__main__":
    init_db()
    print("Бот запущен...")
    bot.polling(none_stop=True)

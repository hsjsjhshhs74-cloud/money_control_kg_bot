import os
import telebot
from telebot import types
from dotenv import load_dotenv



load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

EXPENSES = []
CATEGORIES = ["Еда", "Транспорт", "Развлечения", "Другое"]
temp_expense = {}

def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("➕ Добавить расход", "📜 Показать расходы")
    markup.row("🗂 Выбрать категорию", "❌ Удалить расход")
    markup.row("🧮 Посчитать расходы")
    return markup

def get_categories_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for cat in CATEGORIES:
        markup.add(types.KeyboardButton(cat))
    return markup

@bot.message_handler(commands=['start'])
def cmd_start(message):
    bot.send_message(
        message.chat.id, 
        "Привет! Я бот для учета расходов. Выбери действие в меню:", 
        reply_markup=get_main_keyboard()
    )

@bot.message_handler(func=lambda msg: msg.text == "➕ Добавить расход")
def add_expense_start(message):
    bot.send_message(message.chat.id, "Введите название покупки:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    temp_expense['name'] = message.text
    bot.send_message(message.chat.id, "Введите сумму покупки:")
    bot.register_next_step_handler(message, get_amount)

def get_amount(message):
    try:
        temp_expense['amount'] = float(message.text)
        bot.send_message(message.chat.id, "Выберите категорию:", reply_markup=get_categories_keyboard())
        bot.register_next_step_handler(message, get_category)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите число:")
        bot.register_next_step_handler(message, get_amount)

def get_category(message):
    if message.text in CATEGORIES:
        temp_expense['category'] = message.text
        bot.send_message(message.chat.id, "Введите дату покупки (например, 10.11.2026):", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, get_date)
    else:
        bot.send_message(message.chat.id, "Выберите категорию из списка на кнопках:")
        bot.register_next_step_handler(message, get_category)

def get_date(message):
    temp_expense['date'] = message.text
    EXPENSES.append(temp_expense.copy())
    bot.send_message(
        message.chat.id, 
        f"✅ Расход добавлен:\n{temp_expense['date']} — {temp_expense['name']}: {temp_expense['amount']} руб. ({temp_expense['category']})", 
        reply_markup=get_main_keyboard()
    )

@bot.message_handler(func=lambda msg: msg.text == "📜 Показать расходы")
def show_all_expenses(message):
    if not EXPENSES:
        bot.send_message(message.chat.id, "Список расходов пуст.")
        return
    text = "📋 Все расходы:\n\n"
    for idx, exp in enumerate(EXPENSES, 1):
        text += f"{idx}. {exp['date']} — {exp['name']}: {exp['amount']} руб. ({exp['category']})\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda msg: msg.text == "🗂 Выбрать категорию")
def choose_category_menu(message):
    bot.send_message(message.chat.id, "По какой категории показать расходы?", reply_markup=get_categories_keyboard())
    bot.register_next_step_handler(message, show_filtered_expenses)

def show_filtered_expenses(message):
    category = message.text
    filtered = [exp for exp in EXPENSES if exp["category"] == category]
    if not filtered:
        bot.send_message(message.chat.id, f"В категории '{category}' нет расходов.", reply_markup=get_main_keyboard())
        return
    text = f"📋 Расходы в категории '{category}':\n\n"
    for idx, exp in enumerate(filtered, 1):
        text += f"{idx}. {exp['date']} — {exp['name']}: {exp['amount']} руб.\n"
    bot.send_message(message.chat.id, text, reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda msg: msg.text == "🧮 Посчитать расходы")
def calculate_total(message):
    total = sum(exp["amount"] for exp in EXPENSES)
    bot.send_message(message.chat.id, f"🧮 Общая сумма всех расходов: {total} руб.")

@bot.message_handler(func=lambda msg: msg.text == "❌ Удалить расход")
def delete_expense_menu(message):
    if not EXPENSES:
        bot.send_message(message.chat.id, "Удалять нечего, список пуст.")
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for idx, exp in enumerate(EXPENSES, 1):
        markup.add(types.KeyboardButton(f"Удалить №{idx} — {exp['name']}"))
    bot.send_message(message.chat.id, "Выберите расход для удаления:", reply_markup=markup)
    bot.register_next_step_handler(message, process_deletion)

def process_deletion(message):
    try:
        text = message.text
        idx = int(text.split("№")[1].split(" ")[0]) - 1
        if 0 <= idx < len(EXPENSES):
            removed = EXPENSES.pop(idx)
            bot.send_message(message.chat.id, f"❌ Расход '{removed['name']}' удален.", reply_markup=get_main_keyboard())
        else:
            bot.send_message(message.chat.id, "Ошибка: расход не найден.", reply_markup=get_main_keyboard())
    except Exception:
        bot.send_message(message.chat.id, "Ошибка при удалении. Возврат в меню.", reply_markup=get_main_keyboard())

bot.infinity_polling()

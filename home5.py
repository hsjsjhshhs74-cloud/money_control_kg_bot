import os
import telebot
from telebot import types
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN not found")

bot = telebot.TeleBot(TOKEN)

users_shopping_lists = {}
global_item_counter = 1

def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_add = types.KeyboardButton("➕ Добавить товар")
    btn_my = types.KeyboardButton("🛒 Мои товары")
    btn_del = types.KeyboardButton("🗑 Удалить товар")
    markup.row(btn_add)
    markup.row(btn_my, btn_del)
    return markup

@bot.message_handler(commands=["start"])
def send_welcome(message):
    user_id = message.from_user.id
    if user_id not in users_shopping_lists:
        users_shopping_lists[user_id] = []
    bot.send_message(
        message.chat.id,
        "Привет! Я простой список покупок. Выбирай действие:",
        reply_markup=get_main_keyboard()
    )

@bot.message_handler(func=lambda msg: msg.text == "➕ Добавить товар")
def start_adding(message):
    msg = bot.send_message(message.chat.id, "Введите название товара:")
    bot.register_next_step_handler(msg, get_name)

def get_name(message):
    product_name = message.text
    msg = bot.send_message(message.chat.id, f"Сколько нужно купить '{product_name}'? (например: 2 шт)")
    bot.register_next_step_handler(msg, get_quantity, product_name)

def get_quantity(message, product_name):
    global global_item_counter
    quantity = message.text
    user_id = message.from_user.id

    if user_id not in users_shopping_lists:
        users_shopping_lists[user_id] = []

    new_item = {
        "id": global_item_counter,
        "name": product_name,
        "quantity": quantity
    }
    users_shopping_lists[user_id].append(new_item)
    global_item_counter += 1

    bot.send_message(message.chat.id, f"✅ Добавлено: {product_name} ({quantity})")

@bot.message_handler(func=lambda msg: msg.text == "🛒 Мои товары")
def show_products(message):
    user_id = message.from_user.id
    user_list = users_shopping_lists.get(user_id, [])

    if not user_list:
        bot.send_message(message.chat.id, "Твой список покупок пуст! 🛒")
        return

    text = "📋 **Ваш список покупок:**\n\n"
    for item in user_list:
        text += f"🆔 ID: {item['id']} | **{item['name']}** — {item['quantity']}\n"

    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.text == "🗑 Удалить товар")
def show_delete_menu(message):
    user_id = message.from_user.id
    user_list = users_shopping_lists.get(user_id, [])

    if not user_list:
        bot.send_message(message.chat.id, "Список пуст, нечего удалять.")
        return

    markup = types.InlineKeyboardMarkup()
    for item in user_list:
        button_text = f"{item['name']} ({item['quantity']})"
        callback_data = f"delete_{item['id']}"
        markup.add(types.InlineKeyboardButton(button_text, callback_data=callback_data))

    bot.send_message(message.chat.id, "Нажмите на товар, чтобы удалить его:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_"))
def callback_delete(call):
    user_id = call.from_user.id
    item_id_to_delete = int(call.data.split("_")[1])

    user_list = users_shopping_lists.get(user_id, [])

    for item in user_list:
        if item["id"] == item_id_to_delete:
            user_list.remove(item)
            break

    bot.answer_callback_query(call.id, "Товар удален!")
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="🗑 Товар успешно удален из списка!"
    )

if __name__ == "__main__":
    bot.infinity_polling()

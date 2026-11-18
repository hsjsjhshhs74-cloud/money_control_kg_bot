import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = "9209260762:AAF0lIBafPqQvKXG-uOx4idlwNYCjxKfypE"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

conn = sqlite3.connect("schedule.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS lessons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        day TEXT,
        subject TEXT,
        time TEXT,
        room TEXT
    )
""")
conn.commit()

class AddLesson(StatesGroup):
    day = State()
    subject = State()
    time = State()
    room = State()

DAYS = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Добавить занятие"), KeyboardButton(text="📅 Все расписание")],
        [KeyboardButton(text="🔍 Выбрать день"), KeyboardButton(text="❌ Удалить занятие")]
    ],
    resize_keyboard=True
)

days_reply_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=day)] for day in DAYS],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет! Я бот для хранения расписания. Выбери действие:", reply_markup=main_kb)

@dp.message(F.text == "➕ Добавить занятие")
async def start_add(message: Message, state: FSMContext):
    await message.answer("Выбери день недели:", reply_markup=days_reply_kb)
    await state.set_state(AddLesson.day)

@dp.message(AddLesson.day)
async def add_day(message: Message, state: FSMContext):
    if message.text not in DAYS:
        await message.answer("Пожалуйста, выбери день с помощью кнопок ниже.")
        return
    await state.update_data(day=message.text)
    await message.answer("Введи название предмета:", reply_markup=main_kb)
    await state.set_state(AddLesson.subject)

@dp.message(AddLesson.subject)
async def add_subject(message: Message, state: FSMContext):
    await state.update_data(subject=message.text)
    await message.answer("Введи время занятия (например, 09:00):")
    await state.set_state(AddLesson.time)

@dp.message(AddLesson.time)
async def add_time(message: Message, state: FSMContext):
    await state.update_data(time=message.text)
    await message.answer("Введи номер кабинета:")
    await state.set_state(AddLesson.room)

@dp.message(AddLesson.room)
async def add_room(message: Message, state: FSMContext):
    data = await state.get_data()
    cursor.execute(
        "INSERT INTO lessons (day, subject, time, room) VALUES (?, ?, ?, ?)",
        (data["day"], data["subject"], data["time"], message.text)
    )
    conn.commit()
    await state.clear()
    await message.answer("✅ Занятие успешно добавлено!", reply_markup=main_kb)

@dp.message(F.text == "📅 Все расписание")
async def show_all(message: Message):
    cursor.execute("SELECT day, time, subject, room FROM lessons")
    rows = cursor.fetchall()
    
    if not rows:
        await message.answer("Расписание пока пустое.")
        return

    text = "📚 **Все расписание:**\n\n"
    for day in DAYS:
        day_lessons = [r for r in rows if r == day]
        if day_lessons:
            text += f"🔹 **{day}:**\n"
            for _, time, subj, room in day_lessons:
                text += f"   ⏰ {time} — {subj} (каб. {room})\n"
            text += "\n"
            
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "🔍 Выбрать день")
async def choose_day(message: Message):
    buttons = [[InlineKeyboardButton(text=day, callback_data=f"day_{day}")] for day in DAYS]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("На какой день показать расписание?", reply_markup=kb)

@dp.callback_query(F.data.startswith("day_"))
async def show_day_schedule(callback: CallbackQuery):
    day = callback.data.split("_")[1]
    cursor.execute("SELECT time, subject, room FROM lessons WHERE day = ?", (day,))
    rows = cursor.fetchall()

    if not rows:
        await callback.message.answer(f"На **{day}** занятий нет.", parse_mode="Markdown")
    else:
        text = f"📅 **Расписание на {day}:**\n\n"
        for time, subj, room in rows:
            text += f"⏰ {time} — {subj} (каб. {room})\n"
        await callback.message.answer(text, parse_mode="Markdown")
    
    await callback.answer()

@dp.message(F.text == "❌ Удалить занятие")
async def delete_menu(message: Message):
    cursor.execute("SELECT id, day, time, subject FROM lessons")
    rows = cursor.fetchall()

    if not rows:
        await message.answer("Удалять нечего, список пуст.")
        return

    buttons = []
    for lesson_id, day, time, subj in rows:
        btn_text = f"{day[:2]}. {time} - {subj}"
        buttons.append([InlineKeyboardButton(text=btn_text, callback_data=f"del_{lesson_id}")])

    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Нажми на занятие, чтобы удалить его:", reply_markup=kb)

@dp.callback_query(F.data.startswith("del_"))
async def delete_lesson(callback: CallbackQuery):
    lesson_id = callback.data.split("_")
    cursor.execute("DELETE FROM lessons WHERE id = ?", (lesson_id,))
    conn.commit()
    
    await callback.message.edit_text("🗑 Занятие удалено!")
    await callback.answer()

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

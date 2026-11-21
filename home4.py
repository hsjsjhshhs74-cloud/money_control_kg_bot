import asyncio
import os
import random
from pathlib import Path

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env", override=True)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise SystemExit("Токен не найден: проверь .env, строка BOT_TOKEN=...")


BTN_TOP = "⭐ Топ фильмов"
BTN_HELP = "ℹ️ Помощь"


menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=BTN_TOP),
            KeyboardButton(text=BTN_HELP),
        ]
    ],
    resize_keyboard=True,
)

TOP_TEXT = (
    "<b>Популярные фильмы</b>\n\n"
    "1. Побег из Шоушенка (1994)\n"
    "2. Крёстный отец (1972)\n"
    "3. Тёмный рыцарь (2008)\n"
    "4. Форрест Гамп (1994)\n"
    "5. Начало (2010)\n"
    "6. Интерстеллар (2014)\n"
    "7. 1+1 (2011)\n"
    "8. Матрица (1999)"
)

HELP_TEXT = (
    "<b>Команды кино-бота</b>\n\n"
    "/start — приветствие и описание\n"
    "/help — этот список\n"
    "/top — подборка популярных фильмов\n\n"
    "Кнопки внизу делают то же самое:\n"
    f"{BTN_TOP} — как /top\n"
    f"{BTN_HELP} — как /help\n\n"
    "Можно просто написать «привет» или «спасибо»."
)

UNKNOWN = [
    "Я кинобот, а не переводчик с марсианского 🎬 Напиши /help или нажми кнопку внизу.",
    "Такого фильма в моём зале нет 🍿 За подборкой — /top, за списком команд — /help.",
    "Понял примерно ничего. Зато кнопки внизу понимаю отлично ⭐",
    "Это мимо кассы. Жми «⭐ Топ фильмов» или напиши /help — я как раз это умею.",
]


def is_phrase(phrase: str):
    def check(text: str | None) -> bool:
        if not text:
            return False
        return text.casefold().strip(" !.?,") == phrase

    return check


router = Router()


@router.message(CommandStart())
async def start(message: Message):
    name = message.from_user.first_name
    await message.answer(
        f"Привет, {name}! 🎬\n"
        "Я <b>кино-бот</b>: показываю подборку популярных фильмов "
        "и подсказываю, какие команды есть.\n\n"
        "Напиши /top или нажми «⭐ Топ фильмов».\n"
        "Список команд — /help или кнопка «ℹ️ Помощь».",
        reply_markup=menu,
    )


@router.message(F.text == BTN_HELP)
@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer(HELP_TEXT, reply_markup=menu)


@router.message(F.text == BTN_TOP)
@router.message(Command("top"))
async def top(message: Message):
    await message.answer(TOP_TEXT, reply_markup=menu)


@router.message(F.text.func(is_phrase("привет")))
async def hello(message: Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋 Рад тебя видеть. Что будем смотреть?",
        reply_markup=menu,
    )


@router.message(F.text.func(is_phrase("спасибо")))
async def thanks(message: Message):
    await message.answer(
        "Пожалуйста! 😊 Если нужна ещё подборка — жми «⭐ Топ фильмов» или /top.",
        reply_markup=menu,
    )


@router.message()
async def fallback(message: Message):
    await message.answer(random.choice(UNKNOWN), reply_markup=menu)


async def main():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    print("Кино-бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

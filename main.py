import json
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.filters import CommandStart
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

USERS_FILE = "users.json"


def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=2)


@dp.message(CommandStart())
async def start(message: types.Message):
    users = load_users()
    user_id = str(message.from_user.id)

    # If user already paid
    if users.get(user_id, {}).get("paid"):
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🧠 Open Anki Emulator", web_app=WebAppInfo(url=WEBAPP_URL))]
            ]
        )
        await message.answer("✅ Access granted! Open the app below:", reply_markup=kb)
        return

    # Otherwise show pricing
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💵 1 Month – $1", callback_data="plan_1")],
            [InlineKeyboardButton(text="💵 3 Months – $2", callback_data="plan_3")],
            [InlineKeyboardButton(text="💎 Lifetime – $5", callback_data="plan_life")],
        ]
    )
    await message.answer("Welcome to Anki Emulator!\nChoose your plan to get access 👇", reply_markup=kb)


@dp.callback_query(lambda c: c.data.startswith("plan_"))
async def process_plan(callback: types.CallbackQuery):
    user_id = str(callback.from_user.id)
    users = load_users()
    users[user_id] = {"paid": True}
    save_users(users)

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🧠 Open Anki Emulator", web_app=WebAppInfo(url=WEBAPP_URL))]
        ]
    )

    await callback.message.answer(
        "✅ (TEST MODE) Payment simulated.\nAccess granted! Open the app below:",
        reply_markup=kb,
    )
    await callback.answer()


async def main():
    print("🤖 Bot is running in TEST MODE (no payment integration)")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

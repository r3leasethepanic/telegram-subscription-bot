# run_polling.py
import os
from dotenv import load_dotenv

# Подгружаем .env из корня
load_dotenv()

from aiogram import executor
from bot.handlers import dp

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

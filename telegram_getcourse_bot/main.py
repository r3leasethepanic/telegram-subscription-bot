import logging
from aiogram import Bot, Dispatcher, executor, types
from getcourse_api import create_user_and_order
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TG_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer("Привет! Напиши свой email, чтобы оформить заказ.")

@dp.message_handler()
async def handle_email(message: types.Message):
    email = message.text
    user_created = create_user_and_order(email)
    if user_created:
        await message.answer("Пользователь создан и заказ оформлен! Проверь почту.")
    else:
        await message.answer("Произошла ошибка. Попробуй позже.")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
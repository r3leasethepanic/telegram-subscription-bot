import os
import logging
import base64
import json
import requests
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from getcourse import create_user, create_order

# Логи
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Загрузка .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
# Код продукта по умолчанию, можно вынести в .env
DEFAULT_OFFER = os.getenv("DEFAULT_OFFER_CODE", "7462811")
# Шаги разговорника
ASK_EMAIL, ASK_NAME = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обрабатывает /start, предлагает начать регистрацию"""
    keyboard = [["Начать"]]
    await update.message.reply_text(
        "Добро пожаловать! Чтобы зарегистрироваться и оформить заказ, нажмите кнопку ниже.",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True),
    )
    return ASK_EMAIL

async def ask_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Просит ввести email"""
    # Проверяем, что нажата кнопка Начать
    if update.message.text != "Начать":
        await update.message.reply_text("Нажмите кнопку 'Начать', чтобы продолжить.")
        return ASK_EMAIL
    await update.message.reply_text(
        "Пожалуйста, введите ваш Email:",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ASK_NAME

async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получаем email и просим имя и фамилию"""
    email = update.message.text.strip()
    context.user_data['email'] = email
    await update.message.reply_text("Введите ваше имя и фамилию через пробел, например: Иван Иванов:")
    return ConversationHandler.END if not email else 2

async def process_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Создаёт пользователя и заказ, завершает разговор"""
    name_parts = update.message.text.strip().split()
    if len(name_parts) < 2:
        await update.message.reply_text(
            "Неверный формат. Введите имя и фамилию через пробел:")
        return 2
    first, last = name_parts[0], ' '.join(name_parts[1:])
    email = context.user_data.get('email')

    # Создаём пользователя
    res_user = create_user(email, first, last)
    logging.info("create_user: %s", res_user)
    success_u = res_user.get('success') in (True, 'true')

    # Создаём заказ сразу после
    res_order = create_order(email, DEFAULT_OFFER, float(os.getenv('DEFAULT_OFFER_COST', '0')))
    logging.info("create_order: %s", res_order)
    success_o = res_order.get('success') in (True, 'true')
    link = ''
    if success_o:
        link = res_order.get('result', {}).get('payment_link', '')

    # Формируем сообщение пользователю
    msg = ''
    if success_u and success_o and link:
        msg = f"Спасибо, {first}! Вы зарегистрированы. Вот ссылка на оплату: {link}"
    elif not success_u:
        err = res_user.get('result', {}).get('error_message') or res_user.get('error')
        msg = f"Ошибка при создании пользователя: {err}"
    elif not success_o:
        err = res_order.get('result', {}).get('error_message') or res_order.get('error')
        msg = f"Ошибка при создании заказа: {err}"
    else:
        msg = "Произошла неизвестная ошибка. Попробуйте позже."

    await update.message.reply_text(msg)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена разговора"""
    await update.message.reply_text(
        'Отменено.', reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ASK_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_email)],
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_order)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    app.add_handler(conv)
    logging.info("Bot started with conversation handler.")
    app.run_polling()


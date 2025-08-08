import os
import logging
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

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Загрузка переменных окружения
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DEFAULT_OFFER = os.getenv("DEFAULT_OFFER_CODE")
DEFAULT_COST = float(os.getenv("DEFAULT_OFFER_COST", "0"))

# Шаги разговора
ENTER_EMAIL, ENTER_NAME, ENTER_ORDER = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [["Начать"]]
    await update.message.reply_text(
        "Добро пожаловать! Чтобы зарегистрироваться и оформить заказ, нажмите «Начать».",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return ENTER_EMAIL

async def ask_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text != "Начать":
        await update.message.reply_text("Нажмите «Начать» для старта.")
        return ENTER_EMAIL
    await update.message.reply_text(
        "Пожалуйста, введите ваш Email:",
        reply_markup=ReplyKeyboardRemove()
    )
    return ENTER_NAME

async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    email = update.message.text.strip()
    context.user_data['email'] = email
    await update.message.reply_text("Введите ваше имя и фамилию через пробел, например: Иван Иванов")
    return ENTER_ORDER

async def process_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = update.message.text.strip().split()
    if len(name) < 2:
        await update.message.reply_text("Неверный формат. Введите имя и фамилию через пробел.")
        return ENTER_ORDER
    first, last = name[0], " ".join(name[1:])
    email = context.user_data.get('email')

    # Создаем пользователя
    res_user = create_user(email, first, last)
    logging.info("create_user: %s", res_user)
    # Создаем заказ
    res_order = create_order(email, DEFAULT_OFFER, DEFAULT_COST)
    logging.info("create_order: %s", res_order)

    if res_user.get('success') in (True, 'true') and res_order.get('success') in (True, 'true'):
        link = res_order.get('result', {}).get('payment_link', '')
        await update.message.reply_text(f"Спасибо, {first}! Вы зарегистрированы и заказ создан. Ссылка на оплату:\n{link}")
    else:
        if res_user.get('success') not in (True, 'true'):
            err = res_user.get('result', {}).get('error_message') or res_user.get('error')
            await update.message.reply_text(f"Ошибка при создании пользователя: {err}")
        elif res_order.get('success') not in (True, 'true'):
            err = res_order.get('result', {}).get('error_message') or res_order.get('error')
            await update.message.reply_text(f"Ошибка при создании заказа: {err}")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Регистрация отменена.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ENTER_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_email)],
            ENTER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ENTER_ORDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_order)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    app.add_handler(conv_handler)
    logging.info("Bot started with improved flow.")
    app.run_polling()


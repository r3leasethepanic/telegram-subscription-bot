import os
import logging
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler
from getcourse import create_user, create_order

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Загружаем переменные окружения
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update, context):
    """Обработчик команды /start"""
    await update.message.reply_text(
        "Привет! Я помогу зарегистрироваться в GetCourse и оформить заказ."
    )

async def register(update, context):
    """Обработчик команды /register email имя фамилия"""
    args = context.args
    if len(args) < 3:
        return await update.message.reply_text(
            "Использование: /register email имя фамилия"
        )
    email, first, last = args
    res = create_user(email, first, last)
    logging.info("create_user response: %s", res)
    
    success = res.get("success")
    result = res.get("result", {})
    user_ok = result.get("success")
    
    # Учитываем, что API может возвращать строки или булевы значения
    if success in (True, "true") and user_ok in (True, "true"):
        await update.message.reply_text("Пользователь успешно создан.")
    else:
        # Извлекаем сообщение об ошибке
        err = result.get("error_message") or res.get("error") or res.get("description") or "Неизвестная ошибка"
        await update.message.reply_text(f"Ошибка при создании пользователя: {err}")

async def order(update, context):
    """Обработчик команды /order email код_продукта цена"""
    args = context.args
    if len(args) < 3:
        return await update.message.reply_text(
            "Использование: /order email код_продукта цена"
        )
    email, offer_code, cost_str = args
    try:
        cost = float(cost_str)
    except ValueError:
        return await update.message.reply_text(
            "Ошибка: цена должна быть числом."
        )
    
    res = create_order(email, offer_code, cost)
    logging.info("create_order response: %s", res)
    
    success = res.get("success")
    result = res.get("result", {})
    deal_ok = result.get("success")
    
    if success in (True, "true") and deal_ok in (True, "true"):
        link = result.get("payment_link") or ""
        await update.message.reply_text(f"Ссылка на оплату: {link}")
    else:
        err = result.get("error_message") or res.get("error") or res.get("description") or "Неизвестная ошибка"
        await update.message.reply_text(f"Ошибка при создании заказа: {err}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("register", register))
    app.add_handler(CommandHandler("order", order))
    logging.info("Bot started, polling for updates…")
    app.run_polling()


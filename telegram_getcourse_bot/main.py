import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler
from getcourse import create_user, create_order

# Загружаем переменные окружения из .env
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

    # Проверяем ответ API
    if res.get("success") == "true" and res["result"].get("success") == "true":
        await update.message.reply_text("Пользователь успешно создан.")
    else:
        err = res["result"].get("error_message", "Неизвестная ошибка")
        await update.message.reply_text(
            f"Ошибка при создании пользователя: {err}"
        )

async def order(update, context):
    """Обработчик команды /order email код_продукта цена"""
    args = context.args
    if len(args) < 3:
        return await update.message.reply_text(
            "Использование: /order email код_продукта цена"
        )
    email, offer_code, cost = args
    try:
        cost = float(cost)
    except ValueError:
        return await update.message.reply_text(
            "Ошибка: цена должна быть числом."
        )

    res = create_order(email, offer_code, cost)

    # Проверяем ответ API
    if res.get("success") == "true" and res["result"].get("success") == "true":
        link = res["result"].get("payment_link")
        await update.message.reply_text(f"Ссылка на оплату: {link}")
    else:
        err = res["result"].get("error_message", "Неизвестная ошибка")
        await update.message.reply_text(
            f"Ошибка при создании заказа: {err}"
        )

if __name__ == "__main__":
    # Инициализируем бота и регистрируем обработчики
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("register", register))
    app.add_handler(CommandHandler("order", order))
    # Запускаем polling
    app.run_polling()

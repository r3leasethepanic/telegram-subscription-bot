import os
import logging
import asyncio
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from telegram import Bot
from telegram.error import TelegramError
from db import get_telegram_id

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.DEBUG
)

# Загрузка конфигов
load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')  # ожидается формат -1001234567890

bot = Bot(token=TELEGRAM_TOKEN)
app = Flask(__name__)

@app.route('/payment', methods=['POST'])
def on_payment():
    logging.debug("Received payment webhook: %s", request.data)
    data = request.get_json(force=True, silent=True) or {}
    payment_status = data.get('payment_status')
    email = data.get('email')

    logging.debug("Parsed email=%s, payment_status=%s", email, payment_status)
    if payment_status == 'success' and email:
        tg_id = get_telegram_id(email)
        logging.debug("Lookup tg_id for %s: %s", email, tg_id)
        if tg_id:
            try:
                invite = asyncio.run(
                    bot.create_chat_invite_link(
                        chat_id=CHANNEL_ID,
                        member_limit=1
                    )
                )
                logging.info("Created invite link %s for %s", invite.invite_link, tg_id)
                # Отправка сообщения через HTTP-запрос к Telegram API
                send_resp = requests.post(
                    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                    json={
                        "chat_id": tg_id,
                        "text": f"Оплата подтверждена! Вот ваша ссылка в канал: {invite.invite_link}"
                    }
                )
                logging.info(
                    "Sent invite via HTTP: status %s, response %s",
                    send_resp.status_code,
                    send_resp.text
                )
            except TelegramError as e:
                logging.error("TelegramError: %s", e)
        else:
            logging.warning("No tg_id found for email %s", email)
    else:
        logging.warning("Webhook received with invalid status or missing email: %s", data)
    return jsonify({'ok': True})

if __name__ == '__main__':
    port = int(os.getenv('WEBHOOK_PORT', 5001))
    logging.info("Starting webhook server on port %s", port)
    app.run(host='0.0.0.0', port=port)


# Telegram Subscription Bot + GetCourse

## Установка

1. Клонировать репо и перейти в папку:
   ```bash
   git clone ... && cd telegram-subscription-bot
   ```
2. Создать и активировать venv:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Установить зависимости:
   ```bash
   pip install -r deployment/requirements.txt
   ```
4. Скопировать `.env.example → .env` и заполнить переменные.
5. Запустить:
   ```bash
   uvicorn bot.main:app --host 0.0.0.0 --port 8000
   ```

## Настройка вебхуков

- В Telegram Bot API:
  ```
  setWebhook https://your-domain.com/webhook/telegram/<TELEGRAM_TOKEN>
  ```
- В GetCourse:
  - `order.paid` и `order.cancelled` → `https://your-domain.com/webhook/getcourse`

## Использование

- `/start`
- `/subscribe email name`  
  – получаете ссылку на оплату, после платежа бот сам добавит вас в канал.

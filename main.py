import os
import openai
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Стартовое сообщение
async def start(update: Update, context: CallbackContext):
    message = (
        "Привет! Я помогу вам рассчитать стоимость автомобиля.\n"
        "Пожалуйста, введите параметры автомобиля в следующем формате:\n\n"
        "- Марка\n"
        "- Модель\n"
        "- Год выпуска\n"
        "- Объем двигателя (в литрах)\n\n"
        "Пример: Honda Civic 2021, 1.5 л\n\n"
        "💡 Самые выгодные условия при ввозе авто от 3 до 5 лет."
    )
    await update.message.reply_text(message)

# Команда /help
async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text("Введите параметры автомобиля как указано в /start. Пример: Toyota Camry 2020, 2.0 л")

# Обработка сообщения пользователя
async def handle_message(update: Update, context: CallbackContext):
    user_input = update.message.text

    # Здесь можно использовать парсинг через GPT, BeautifulSoup и т.п. 
    # Сейчас просто пример с заготовленными данными:
    brand = "Honda"
    model = "Civic"
    year = 2021
    engine_liters = 1.5
    engine_cm3 = int(engine_liters * 1000) - 2  # уменьшаем на 2 см³

    # Средняя цена с сайта (пока заглушка)
    car_price_cny = 89800  # В будущем заменим на скрейпинг с сайта
    exchange_rate = 13  # Примерный курс юаня к рублю
    car_price_rub = car_price_cny * exchange_rate

    # Расчёт пошлины по таблице для 3-5 лет
    if engine_cm3 <= 1000:
        duty = engine_cm3 * 1.5
    elif engine_cm3 <= 1500:
        duty = engine_cm3 * 1.7
    elif engine_cm3 <= 1800:
        duty = engine_cm3 * 2.5
    elif engine_cm3 <= 2300:
        duty = engine_cm3 * 2.7
    elif engine_cm3 <= 3000:
        duty = engine_cm3 * 3
    else:
        duty = engine_cm3 * 3.6

    # Комиссии
    commission_hidden = car_price_cny * 0.15  # Не показываем
    commission_invoice = car_price_cny * 0.025
    delivery_total = (15000 + commission_hidden) * exchange_rate
    recycle_fee = 3400  # Фиксированный сбор

    total = car_price_rub + duty + commission_invoice * exchange_rate + delivery_total + recycle_fee

    response = (
        f"📄 Параметры: {brand} {model} {year}, {engine_cm3} см³\n"
        f"💰 Средняя цена: ¥{car_price_cny} (~{car_price_rub:,.0f} ₽)\n"
        f"📦 Доставка + проверка: ~{delivery_total:,.0f} ₽\n"
        f"🧾 Комиссия за инвойс: ~{commission_invoice * exchange_rate:,.0f} ₽\n"
        f"🛃 Пошлина: ~{duty:,.0f} ₽\n"
        f"♻️ Утилизационный сбор: {recycle_fee} ₽\n\n"
        f"💸 Итоговая стоимость: ~{total:,.0f} ₽\n\n"
        f"📩 Свяжитесь с менеджером: @your_manager\n"
        f"🖼️ Фото авто: [в разработке]"
    )
    await update.message.reply_text(response)

# Запуск приложения
async def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

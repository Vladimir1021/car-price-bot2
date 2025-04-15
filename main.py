import os
import openai
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Загрузка переменных окружения из .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Стартовое сообщение
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "Привет! Я помогу рассчитать стоимость автомобиля, импортируемого из Китая в Россию.\n"
        "Пожалуйста, введите данные в формате:\n"
        "Марка\nМодель\nГод выпуска\nОбъем двигателя (в литрах)\n\n"
        "Пример:\nToyota Camry\n2020\n2.5"
    )
    await update.message.reply_text(message)

# Расчёт стоимости авто
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    lines = text.split("\n")

    if len(lines) < 4:
        await update.message.reply_text("Пожалуйста, введите все четыре параметра.")
        return

    brand = lines[0]
    model = lines[1]
    try:
        year = int(lines[2])
        engine_liters = float(lines[3].replace(",", "."))
    except ValueError:
        await update.message.reply_text("Год выпуска и объем двигателя должны быть числами.")
        return

    # Уменьшаем объём на 2 см³ по инструкции
    engine_cm3 = int(engine_liters * 1000) - 2

    # Средняя цена — пока заглушка (можно потом заменить на запрос на сайт)
    car_price_cny = 89800
    exchange_rate = 13
    car_price_rub = car_price_cny * exchange_rate

    # Примерная пошлина (20% от стоимости)
    customs_fee = 0.2 * car_price_rub

    # Дополнительные расходы (заглушки)
    delivery = 80000
    inspection = 10000
    invoice_commission = 15000
    recycling_fee = 5200

    final_price = car_price_rub + customs_fee + delivery + inspection + invoice_commission + recycling_fee

    response = (
        f"Марка: {brand}\nМодель: {model}\nГод выпуска: {year}\nОбъём: {engine_liters} л ({engine_cm3} см³)\n\n"
        f"Средняя цена в Китае: {car_price_cny} ¥ → {car_price_rub:.0f} ₽\n"
        f"Таможенная пошлина: {customs_fee:.0f} ₽\n"
        f"Доставка: {delivery} ₽\nПроверка: {inspection} ₽\nКомиссия за инвойс: {invoice_commission} ₽\nУтилизационный сбор: {recycling_fee} ₽\n\n"
        f"Итоговая стоимость: {final_price:.0f} ₽"
    )

    await update.message.reply_text(response)

# Помощь
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Просто введите параметры автомобиля, и я рассчитаю стоимость. Напишите /start для начала.")

async def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except RuntimeError:
        import nest_asyncio
        nest_asyncio.apply()
        asyncio.get_event_loop().run_until_complete(main())

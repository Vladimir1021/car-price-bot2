import os
import openai
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import asyncio
import nest_asyncio  # Импортируем nest_asyncio

# Применяем nest_asyncio, чтобы избежать ошибок с циклом событий
nest_asyncio.apply()  # Это позволит использовать один цикл событий

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

# Получение средней цены автомобиля через GPT
async def get_car_price_from_gpt(brand, model, year):
    prompt = (
        f"Какова средняя рыночная цена в юанях на автомобиль {brand} {model} {year} года выпуска,"
        " если он покупается в Китае для экспорта в Россию? Укажи только число, без текста."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты автоэксперт, специализирующийся на импорте автомобилей из Китая в Россию."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=20,
        )
        price_str = response.choices[0].message.content.strip().replace("¥", "").replace(",", "")
        return float(price_str)
    except Exception as e:
        print(f"GPT ERROR: {e}")  # Логирование ошибки GPT
        return 89800  # fallback на заглушку

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

    engine_cm3 = int(engine_liters * 1000) - 2

    # Получение средней цены через GPT
    car_price_cny = await get_car_price_from_gpt(brand, model, year)
    exchange_rate = 13
    car_price_rub = car_price_cny * exchange_rate

    customs_fee = 0.2 * car_price_rub
    delivery = 80000
    inspection = 10000
    invoice_commission = 15000
    recycling_fee = 5200

    final_price = car_price_rub + customs_fee + delivery + inspection + invoice_commission + recycling_fee

    response = (
        f"Марка: {brand}\nМодель: {model}\nГод выпуска: {year}\nОбъём: {engine_liters} л ({engine_cm3} см³)\n\n"
        f"Средняя цена в Китае: {car_price_cny:.0f} ¥ → {car_price_rub:.0f} ₽\n"
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

    await application.run_polling()  # Убираем параметр port

if __name__ == "__main__":
    asyncio.run(main())  # используем asyncio.run для запуска основного приложения

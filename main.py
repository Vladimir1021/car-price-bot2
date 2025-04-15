import os
import openai
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import nest_asyncio

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
    keyboard = [["Уточнить данные"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(message, reply_markup=reply_markup)

# Помощь
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Просто введите параметры автомобиля, и я рассчитаю стоимость. Напишите /start для начала.")

# Запрос к GPT для расчета
async def query_gpt(prompt: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Ты эксперт по автопошлинам и импорту авто из Китая в Россию."},
            {"role": "user", "content": prompt},
        ]
    )
    return response.choices[0].message.content.strip()

# Обработка текста от пользователя
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text.lower() in ["уточнить данные"]:
        await update.message.reply_text("Хорошо, введите данные заново в формате:\nМарка\nМодель\nГод выпуска\nОбъем двигателя (л)")
        return

    lines = text.split("\n")
    if len(lines) < 4:
        await update.message.reply_text("Пожалуйста, введите все четыре параметра.")
        return

    brand, model = lines[0], lines[1]
    try:
        year = int(lines[2])
        engine_liters = float(lines[3].replace(",", "."))
    except ValueError:
        await update.message.reply_text("Год выпуска и объем двигателя должны быть числами.")
        return

    engine_cm3 = int(engine_liters * 1000) - 2

    gpt_prompt = (
        f"Рассчитай стоимость автомобиля, импортируемого из Китая в Россию.\n"
        f"Марка: {brand}\nМодель: {model}\nГод выпуска: {year}\nОбъем двигателя: {engine_liters} л ({engine_cm3} см³).\n"
        "Укажи стоимость в юанях и рублях, пошлину, доставку, проверку, утилизационный сбор, комиссии и итоговую сумму."
    )

    try:
        result = await query_gpt(gpt_prompt)
        await update.message.reply_text(result)
    except Exception as e:
        await update.message.reply_text("Ошибка при обращении к GPT. Попробуйте позже.")
        print("GPT ERROR:", e)

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
        nest_asyncio.apply()
        asyncio.get_event_loop().run_until_complete(main())

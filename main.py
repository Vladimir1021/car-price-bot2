import os
import openai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Инициализация OpenAI
openai.api_key = OPENAI_API_KEY

# Стартовое сообщение с инструкцией
async def start(update: Update, context: CallbackContext):
    message = (
        "Привет! Я помогу вам рассчитать стоимость автомобиля. "
        "Пожалуйста, введите параметры автомобиля в следующем формате:\n\n"
        "- Марка\n"
        "- Модель\n"
        "- Год выпуска\n"
        "- Объем двигателя\n\n"
        "Пример: Honda Civic 2021, 1.5 л."
    )
    await update.message.reply_text(message)

# Обработка ввода параметров автомобиля и расчет стоимости
async def handle_message(update: Update, context: CallbackContext):
    car_info = update.message.text.strip()
    
    # Получаем рыночную цену с сайта (здесь пока заглушка)
    market_price = 89800  # Используем цену с сайта для примера
    
    # Пример расчета (упрощенный)
    exchange_rate_cny = 13  # Примерный курс юаня
    price_in_rubles = market_price * exchange_rate_cny
    customs_fee = 0.2 * price_in_rubles  # Примерная пошлина 20%
    final_price = price_in_rubles + customs_fee
    
    response = f"Вы ввели следующие данные:\n{car_info}\n\n"
    response += f"Рыночная стоимость: {price_in_rubles:.2f} рублей\n"
    response += f"Таможенная пошлина: {customs_fee:.2f} рублей\n"
    response += f"Итоговая стоимость: {final_price:.2f} рублей"
    
    await update.message.reply_text(response)

# Функция для обработки команды /help
async def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Я помогу вам рассчитать стоимость автомобиля.\n"
        "Введите информацию о машине, как показано в примере:\n\n"
        "- Марка\n"
        "- Модель\n"
        "- Год выпуска\n"
        "- Объем двигателя\n\n"
        "Команды:\n"
        "/start - инструкция\n"
        "/help - помощь\n"
    )

def main():
    # Создание объекта Application и передача токена
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Добавление обработчиков команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Обработчик текстовых сообщений для расчета стоимости
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()

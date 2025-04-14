
import os
import openai
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Инициализация OpenAI
openai.api_key = OPENAI_API_KEY

# Стартовое сообщение с инструкцией
def start(update: Update, context: CallbackContext):
    message = (
        "Привет! Я помогу вам рассчитать стоимость автомобиля. "
        "Пожалуйста, введите параметры автомобиля в следующем формате:

"
        "- Марка
"
        "- Модель
"
        "- Год выпуска
"
        "- Объем двигателя

"
        "Пример: Honda Civic 2021, 1.5 л."
    )
    update.message.reply_text(message)

# Обработка ввода параметров автомобиля и расчет стоимости
def handle_message(update: Update, context: CallbackContext):
    car_info = update.message.text.strip()
    
    # Получаем рыночную цену с сайта (здесь пока заглушка)
    market_price = 89800  # Используем цену с сайта для примера
    
    # Пример расчета (упрощенный)
    exchange_rate_cny = 13  # Примерный курс юаня
    price_in_rubles = market_price * exchange_rate_cny
    customs_fee = 0.2 * price_in_rubles  # Примерная пошлина 20%
    final_price = price_in_rubles + customs_fee
    
    response = f"Вы ввели следующие данные:
{car_info}

"
    response += f"Рыночная стоимость: {price_in_rubles:.2f} рублей
"
    response += f"Таможенная пошлина: {customs_fee:.2f} рублей
"
    response += f"Итоговая стоимость: {final_price:.2f} рублей"
    
    update.message.reply_text(response)

# Функция для обработки команды /help
def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Я помогу вам рассчитать стоимость автомобиля.
"
        "Введите информацию о машине, как показано в примере:
"
        "- Марка
"
        "- Модель
"
        "- Год выпуска
"
        "- Объем двигателя

"
        "Команды:
"
        "/start - инструкция
"
        "/help - помощь
"
    )

def main():
    # Создание объекта Updater и передача токена
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # Добавление обработчиков команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    
    # Обработчик текстовых сообщений для расчета стоимости
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

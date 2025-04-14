
import requests

# Ваш токен Telegram-бота
TOKEN = "7556724021:AAFIXoUrussVLFuN4yUZpwIijer7lrov1Tg"

# Формируем URL для запроса
url = f"https://api.telegram.org/bot{TOKEN}/deleteWebhook"

# Отправляем GET-запрос
response = requests.get(url)

# Выводим ответ, чтобы понять результат
print(response.json())

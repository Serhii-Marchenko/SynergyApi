import requests
import config


def send_telegram_message_with_inline_button(chat_id, text):


    url = f"https://api.telegram.org/bot{config.API_TOKEN}/sendMessage"

    # Создаем структуру для кнопки
    payload = {
        'chat_id': chat_id,
        'text': text,
    }
    response = requests.post(url, data=payload)
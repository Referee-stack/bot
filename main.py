import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()


TOKEN = os.getenv('TELEGRAM_TOKEN')
URL = f"https://api.telegram.org/bot{TOKEN}"


def render_progressbar(total, iteration, prefix='', suffix='', length=30,
                       fill='█', zfill='░'):
    iteration = min(total, iteration)
    percent = "{0:.1f}".format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    pbar = fill * filled_length + zfill * (length - filled_length)
    return '{0} |{1}| {2}% {3}'.format(prefix, pbar, percent, suffix)


def main():
    last_id = 0

    while True:
        try:
            params = {'offset': last_id + 1}
            response = requests.get(f"{URL}/getUpdates", params=params)
            updates = response.json()

            for update in updates.get('result', []):
                last_id = update['update_id']
                message = update.get('message', {})

                if message.get('text'):
                    chat_id = message['chat']['id']
                    text = message['text']

                    if text == '/start':
                        data = {'chat_id': chat_id,
                                'text': "Отправь число секунд для таймера"}
                        requests.post(f"{URL}/sendMessage", json=data)

                    elif text.isdigit():
                        seconds = int(text)
                        if 1 <= seconds <= 3600:
                            data = {'chat_id': chat_id,
                                    'text': "Запуск таймера..."}
                            response = requests.post(f"{URL}/sendMessage",
                                                     json=data)
                            message_id = response.json()['result']['message_id']

                            for remaining in range(seconds, 0, -1):
                                elapsed = seconds - remaining
                                progress_text = render_progressbar(
                                    seconds, elapsed, '⏰', f'{remaining}с')
                                data = {
                                    'chat_id': chat_id,
                                    'message_id': message_id,
                                    'text': progress_text
                                }
                                requests.post(f"{URL}/editMessageText",
                                              json=data)
                                time.sleep(1)

                            data = {
                                'chat_id': chat_id,
                                'message_id': message_id,
                                'text': "Время вышло"
                            }
                            requests.post(f"{URL}/editMessageText", json=data)

            time.sleep(1)

        except Exception:
            time.sleep(5)


if __name__ == '__main__':
    main()

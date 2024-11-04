import os
import pickle
import logging
from datetime import date, datetime
from typing import Optional, List, Tuple
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
import config
import functions as fn
from bx import get_chat_ids, filter_items_by_frequency
import threading

app = FastAPI()

# путь для файла
# PICKLE_FILE = "scheduled_tasks.pkl"
# путь для файла в docker
PICKLE_FILE = "/app/scheduled_tasks.pkl"
# Логирование
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

internal_logger = logging.getLogger("internal")
client_logger = logging.getLogger("client")

internal_log_filename = 'internal.log'
client_log_filename = 'error.log'

if not internal_logger.handlers:  # Проверяем, нет ли уже добавленных обработчиков
    internal_logger_handler = logging.FileHandler(filename=os.path.join(log_directory, internal_log_filename),
                                                  encoding='utf-8')
    internal_logger.addHandler(internal_logger_handler)
    internal_logger.setLevel(logging.DEBUG)

if not client_logger.handlers:  # Проверяем, нет ли уже добавленных обработчиков
    client_log_handler = logging.FileHandler(filename=os.path.join(log_directory, client_log_filename),
                                             encoding='utf-8')
    client_logger.addHandler(client_log_handler)
    client_logger.setLevel(logging.DEBUG)


class Recipient(BaseModel):
    restName: str
    numberOfVisitsFrom: int
    numberOfVisitsTo: int
    dateVisitFrom: date
    dateVisitTo: date
    textMessage: str
    linkImage: str
    textButton: Optional[str] = None
    linkButton: Optional[str] = None
    # reply_markup: Optional[dict] = None
    timeToStartSending: Optional[datetime] = None


def save_tasks(tasks: List[Tuple[dict, str]]):
    """Сохраняет задачи в файл."""
    with open(PICKLE_FILE, "wb") as f:
        pickle.dump(tasks, f)


def load_tasks() -> List[Tuple[dict, str]]:
    """Загружает задачи из файла."""
    if os.path.exists(PICKLE_FILE):
        with open(PICKLE_FILE, "rb") as f:
            return pickle.load(f)
    return []


async def execute_task(item: Recipient):
    """Функция для выполнения задачи отправки сообщений"""
    start = datetime.now()
    internal_logger.error(f"Начало задачи: {start}")

    try:
        download_link = await fn.extract_file_id(item.linkImage)
        file_path = await fn.download_foto(download_link)
        internal_logger.info(f"Файл загружен: {file_path}")

        deals = get_chat_ids(rest_name=item.restName, date_from=item.dateVisitFrom, date_to=item.dateVisitTo)
        chatIds = filter_items_by_frequency(number_from=item.numberOfVisitsFrom, number_to=item.numberOfVisitsTo,
                                            data=deals)
        if item.textButton and item.linkButton is not None:
            reply_markup = {
                        "inline_keyboard": [
                            [
                                {"text": item.textButton, "url": item.linkButton}
                            ]
                        ]
                    }
        else:
            reply_markup = None

        result_send = await fn.send_photo(chatIds, file_path, config.API_TOKEN, item.textMessage, reply_markup)
        os.remove(file_path)

        end = datetime.now()
        duration = (end - start).total_seconds()
        internal_logger.error(f"Прошло: {duration} секунд")
        internal_logger.info(f"Задача '{item.textMessage}' выполнена успешно.")

        return {'result_send': result_send, "start": start, "end": end}
    except Exception as e:
        internal_logger.error(f"Ошибка при выполнении задачи: {str(e)}")
        return {"error": str(e)}


def schedule_task(item: Recipient, run_time: datetime):
    """Планирует выполнение задачи на указанное время."""
    delay = (run_time - datetime.now()).total_seconds()
    internal_logger.info(f"Планирование задачи на {item.textMessage} с задержкой {delay} секунд.")

    if delay > 0:
        timer = threading.Timer(delay, lambda: asyncio.run(execute_task(item)))
        timer.start()
        internal_logger.info(f"Задача '{item.textMessage}' запланирована на {run_time}.")
    else:
        internal_logger.warning(f"Время для задачи уже прошло: {item}")


@app.post("/api/send")
async def schedule_task_endpoint(item: Recipient):
    print("Сработал эндпоинт")
    """Эндпоинт для создания задачи отправки на запланированное время"""
    if item.timeToStartSending:
        internal_logger.info(f"Запланирована задача на: {item.timeToStartSending}")
        tasks = load_tasks()


        # Сохраняем словарь, а не объект Recipient
        tasks.append((item.dict(), item.timeToStartSending.isoformat()))  # Преобразуем в строку ISO 8601
        save_tasks(tasks)

        schedule_task(item, item.timeToStartSending)
        return {"message": f"Задача запланирована на {item.timeToStartSending}"}
    else:
        # Если время не указано, выполнить сразу
        result = await execute_task(item)
        return result


@app.get('/')
def index():
    return "Server is running"

def run_pending_tasks():
    """Загружает и планирует все задачи при запуске сервера"""
    print("Попытка загрузки задач из файла")
    tasks = load_tasks()
    print("Загруженные задачи:", tasks)  # Добавлен вывод всех загруженных задач

    if not tasks:
        print("Нет задач для восстановления.")
        return

    future_tasks = []
    for item_dict, run_time_str in tasks:
        run_time = datetime.fromisoformat(run_time_str)  # Преобразуем строку в datetime
        print(f"Проверка задачи с временем запуска: {run_time}")

        # Проверка: если время уже прошло, не добавляем задачу в будущие задачи
        if run_time > datetime.now():
            item = Recipient(**item_dict)  # Создаем объект Recipient из словаря
            print(f"Запланирована задача: {item.textMessage} на {run_time}")
            internal_logger.info(f"Загружена задача: {item.textMessage} на {run_time}")
            schedule_task(item, run_time)
            future_tasks.append((item_dict, run_time_str))
        else:
            internal_logger.warning(f"Удалена задача с прошедшим временем: {run_time}")
            print(f"Удалена задача с прошедшим временем: {run_time}")

    # Сохраняем только будущие задачи
    save_tasks(future_tasks)
    print("Сохранены задачи на будущее:", future_tasks)


if __name__ == "__main__":
    run_pending_tasks()  # Запуск восстановления задач в фоне
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
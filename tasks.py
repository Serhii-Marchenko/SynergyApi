import os
import threading
import asyncio
from datetime import datetime
import logging_setup
from bx import get_chat_ids, filter_items_by_frequency
import functions as fn
from models import Recipient
import config
import db_sending
import threading
internal_logger = logging_setup.internal_logger


# Глобальный словарь для хранения запланированных задач
scheduled_tasks = {}

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
        # result_send = chatIds
        # print(result_send)
        os.remove(file_path)

        end = datetime.now()
        duration = (end - start).total_seconds()
        internal_logger.error(f"Прошло: {duration} секунд")
        internal_logger.info(f"Задача '{item.textMessage}' выполнена успешно.")

        return {'result_send': result_send, "start": start, "end": end}
    except Exception as e:
        internal_logger.error(f"Ошибка при выполнении задачи: {str(e)}")
        return {"error": str(e)}

# def schedule_task(item: Recipient, run_time: datetime):
#     """Запускает задачу с отложенным выполнением"""
#     delay = (run_time - datetime.now()).total_seconds()
#     if delay > 0:
#         task_timer = threading.Timer(delay, lambda: asyncio.run(execute_task(item)))
#         task_timer.start()
#         scheduled_tasks[item.id] = task_timer  # Сохраняем задачу по ID
#         internal_logger.info(f"Задача с ID {item.id} запланирована на {run_time}.")
#     else:
#         internal_logger.warning(f"Время для задачи уже прошло: {item}")
# def schedule_task(item: Recipient, run_time: datetime, task_id):
#     """Запускает задачу и сохраняет её в глобальный словарь"""
#     delay = (run_time - datetime.now()).total_seconds()
#     if delay > 0:
#         task_timer = threading.Timer(delay, lambda: asyncio.run(execute_task(item)))
#         task_timer.start()
#         scheduled_tasks[task_id] = task_timer  # Используем task_id вместо item.id
#         print(scheduled_tasks)
#         internal_logger.info(f"Задача с ID {task_id} запланирована на {run_time}.")
#     else:
#         internal_logger.warning(f"Время для задачи уже прошло: {item}")



# async def schedule_task(item: Recipient, run_time: datetime, task_id):
#     """Запускает асинхронную задачу"""
#     delay = (run_time - datetime.now()).total_seconds()
#     if delay > 0:
#         await asyncio.sleep(delay)  # Асинхронная задержка
#     await execute_task(item)  # Запускаем задачу без потока
#     internal_logger.info(f"Задача с ID {task_id} выполнена.")
# def cancel_scheduled_task(task_id: int):
#     """Отменяет только одну конкретную задачу по ID"""
#     task = scheduled_tasks.pop(task_id, None)
#
#     if task:
#
#         task.cancel()  # Останавливаем таймер
#         internal_logger.info(f"Задача с ID {task_id} отменена.")
#     else:
#         internal_logger.warning(f"Задача с ID {task_id} не найдена.")
#
# # def run_pending_tasks():
# #     import db_sending
# #     tasks = db_sending.get_all_pending_tasks()
# #     print("Запланированные задачи:", tasks)
# #
# #     if not tasks:
# #         print('Нет запланированых задач')
# #         internal_logger.info("Нет ожидающих задач.")
# #         return
# #
# #     for task in tasks:
# #         item_dict, run_time = task
# #         run_time = datetime.fromisoformat(run_time)
# #         if run_time > datetime.now():
# #             item = Recipient(**item_dict)
# #             schedule_task(item, run_time)
#

async def schedule_task(item: Recipient, run_time: datetime, task_id: str):
    delay = (run_time - datetime.now()).total_seconds()
    if delay > 0:
        try:
            internal_logger.info(f"Задача с ID {task_id} запланирована на {run_time}.")
            await asyncio.sleep(delay)
        except asyncio.CancelledError:
            internal_logger.info(f"Задача с ID {task_id} была отменена.")
            return
    await execute_task(item)
    internal_logger.info(f"Задача с ID {task_id} завершена.")
    scheduled_tasks.pop(task_id, None)

# Функция запуска задачи
def start_task(item: Recipient, run_time: datetime, task_id: str):
    task = asyncio.create_task(schedule_task(item, run_time, task_id), name=task_id)
    print(task)
    # scheduled_tasks[task_id] = task
    internal_logger.info(f"Задача с ID {task_id} добавлена в очередь.")
    # print(scheduled_tasks)

# Функция отмены задачи
def get_task_by_name(task_name):
    for task in asyncio.all_tasks():
        if task.get_name() == task_name:
            return task
    return None
def cancel_scheduled_task(task_id: str):
    task = get_task_by_name(task_id)
    print('Отменяем задачу',task)
    if task:
        task.cancel()
        internal_logger.info(f"Задача {task_id} отменена.")
    else:
        internal_logger.warning(f"Задача {task_id} не найдена.")


async def run_pending_tasks():

    """Загружает и планирует все задачи при запуске сервера"""
    tasks = db_sending.get_all_pending_tasks()

    if not tasks:
        internal_logger.info("Нет ожидающих задач.")
        print('Нет запланированых задач')
        return

    internal_logger.info(f"Запланированные задачи: {tasks}")

    for task in tasks:
        print('Запланирована задача:', task)
        try:
            # Преобразуем данные в объект модели `Recipient`
            item = Recipient(
                phone=task["phone_user"],
                restName=task["rest"],
                numberOfVisitsFrom=task["number_of_visits_from"],
                numberOfVisitsTo=task["number_of_visits_to"],
                dateVisitFrom=task["date_visit_from"],
                dateVisitTo=task["date_visit_to"],
                textMessage=task["text_message"],
                linkImage=task["link_image"],
                textButton=task.get("text_button"),
                linkButton=task.get("link_button"),
                timeToStartSending=task["time_to_start_sending"]
            )

            run_time = task["time_to_start_sending"]
            if isinstance(run_time, str):
                run_time = datetime.fromisoformat(run_time)  # Преобразуем строку в datetime
            task_id = str(task["id"])

            if run_time > datetime.now():
                # schedule_task(item, run_time,task_id)
                # asyncio.create_task(schedule_task(item, run_time, task_id))
                start_task(item, run_time,task_id)
            else:
                internal_logger.warning(f"Время задачи уже прошло: {item.textMessage} (ID: {task['id']})")

        except Exception as e:
            internal_logger.error(f"Ошибка при обработке задачи {task}: {str(e)}")

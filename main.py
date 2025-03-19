# import os
# import logging
# from datetime import date, datetime
# from typing import Optional, List, Tuple
# import uvicorn
# from pydantic import BaseModel
# import asyncio
# import config
# import functions as fn
# from bx import get_chat_ids, filter_items_by_frequency
# import threading
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi import FastAPI
# from fastapi.responses import FileResponse
# import db_user
# import db_sending
# import requests
# from models import Send, User, Recipient,UserPhone
# from logging_setup import internal_logger
#
# # Путь к папке с вашими статическими файлами
# static_directory = os.path.join(os.path.dirname(__file__), "frontend")
# app = FastAPI()
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Разрешает доступ с любого источника (можно указать конкретные)
#     allow_credentials=True,
#     allow_methods=["*"],  # Разрешает все методы (GET, POST, PUT, DELETE)
#     allow_headers=["*"],  # Разрешает любые заголовки
# )
#
#
#
# def send_telegram_message_with_inline_button(chat_id, text):
#
#     url = f"https://api.telegram.org/bot{config.API_TOKEN}/sendMessage"
#
#     # Создаем структуру для кнопки
#     payload = {
#         'chat_id': chat_id,
#         'text': text,
#     }
#
#     response = requests.post(url, data=payload)
#
# async def execute_task(item: Recipient):
#     """Функция для выполнения задачи отправки сообщений"""
#     start = datetime.now()
#     internal_logger.info(f"Начало задачи: {start}")  # Изменил на INFO для начала выполнения задачи
#
#     try:
#         download_link = await fn.extract_file_id(item.linkImage)
#         file_path = await fn.download_foto(download_link)
#         internal_logger.info(f"Файл загружен: {file_path}")
#
#         deals = get_chat_ids(rest_name=item.restName, date_from=item.dateVisitFrom, date_to=item.dateVisitTo)
#         chatIds = filter_items_by_frequency(number_from=item.numberOfVisitsFrom, number_to=item.numberOfVisitsTo,
#                                             data=deals)
#         if item.textButton and item.linkButton is not None:
#             reply_markup = {
#                 "inline_keyboard": [
#                     [
#                         {"text": item.textButton, "url": item.linkButton}
#                     ]
#                 ]
#             }
#         else:
#             reply_markup = None
#
#         result_send = await fn.send_photo(chatIds, file_path, config.API_TOKEN, item.textMessage, reply_markup)
#         os.remove(file_path)
#
#         end = datetime.now()
#         duration = (end - start).total_seconds()
#         internal_logger.info(f"Прошло: {duration} секунд")  # Изменил на INFO для завершения задачи
#         internal_logger.info(f"Задача '{item.textMessage}' выполнена успешно.")
#
#         return {'result_send': result_send, "start": start, "end": end}
#     except Exception as e:
#         internal_logger.error(f"Ошибка при выполнении задачи: {str(e)}")
#         return {"error": str(e)}
#
#
# def schedule_task(item: Recipient, run_time: datetime):
#     """Планирует выполнение задачи на указанное время."""
#     delay = (run_time - datetime.now()).total_seconds()
#     internal_logger.info(f"Планирование задачи на {item.textMessage} с задержкой {delay} секунд.")
#
#     if delay > 0:
#         timer = threading.Timer(delay, lambda: asyncio.run(execute_task(item)))
#         timer.start()
#         internal_logger.info(f"Задача '{item.textMessage}' запланирована на {run_time}.")
#     else:
#         internal_logger.warning(f"Время для задачи уже прошло: {item}")
#
#
# @app.post('/delete-send')
# async def delete_send(item: Send):
#     result = db_sending.delete_record_by_id(item.id)
#     if result:
#         internal_logger.info(f"Запись с ID {item.id} удалена.")
#         return {'success': True}
#     else:
#         internal_logger.warning(f"Не удалось удалить запись с ID {item.id}.")
#         return {'success': False}
#
#
# @app.post('/get-sends')
# async def get_sends(item: UserPhone):
#     all_data = db_sending.get_all_records_by_phone_number(item.phone)
#     departments = {
#         '325':'BEERTEKA',
#         '326':'YUG',
#         '371':'TERRACE' ,
#         '372':'REEF',
#         '384':'ROASTERY' ,
#         '5971':'CAFE CENTRAL',
#         '8204':'MEDITERRANEAN'
#     }
#     list_all_data = []
#     for item in all_data:
#         dict_data = {
#             "ID": item[0],
#             "Заведение": departments[item[2]],
#             "Посещений От": item[3],
#             "Посещений До": item[4],
#             "Дата посещения От": item[5],
#             "Дата посещения До": item[6],
#             "Текст сообщения": item[7],
#             'Cсылка картинки': item[8],
#             'Текст кнопки': item[9],
#             'Ссылка кнопки': item[10],
#             'Дата рассылки': item[11],
#             'Дата создания': item[12]
#         }
#         list_all_data.append(dict_data)
#
#     internal_logger.info(f"Получены данные по телефону {item.phone}")
#     return {'success': True, 'list': list_all_data}
#
#
# @app.post("/api/send")
# async def schedule_task_endpoint(item: Recipient):
#     db_sending.create_record(phone_number=item.phone,
#                              rest=item.restName,
#                              number_of_visits_from=item.numberOfVisitsFrom,
#                              number_of_visits_to=item.numberOfVisitsTo,
#                              date_visit_from=item.dateVisitFrom,
#                              date_visit_to=item.dateVisitTo,
#                              text_message=item.textMessage,
#                              link_image=item.linkImage,
#                              text_button=item.textButton,
#                              link_button=item.linkButton,
#                              time_to_start_sending=item.timeToStartSending)
#
#     """Эндпоинт для создания задачи отправки на запланированное время"""
#     if item.timeToStartSending:
#         internal_logger.info(f"Запланирована задача на: {item.timeToStartSending}")
#         schedule_task(item, item.timeToStartSending)
#         return {"message": f"Задача запланирована на {item.timeToStartSending}"}
#     else:
#         # Если время не указано, выполнить сразу
#         result = await execute_task(item)
#         return result
#
#
# @app.get("/")
# async def get_index():
#     # Отдаем файл index.html
#     return FileResponse(os.path.join(static_directory, "index.html"))
#
#
# @app.get("/frontend/{file_name}")
# async def get_static_file(file_name: str):
#     file_path = os.path.join(static_directory, file_name)
#     if os.path.exists(file_path):
#         return FileResponse(file_path)
#     return {"error": "File not found"}
#
#
# @app.post("/send-code")
# async def root(user: User):
#     id_tg = db_user.get_user_by_phone(user.phone)
#     if id_tg is None:
#         return {"success": False}
#     else:
#         send_telegram_message_with_inline_button(id_tg, f"Ваш код: {user.code}")
#         internal_logger.info(f"Код отправлен пользователю с телефоном {user.phone}")
#         return {"success": True, "id_tg": id_tg}
#
#
# def run_pending_tasks():
#     """Загружает и планирует все задачи при запуске сервера"""
#     tasks = db_sending.get_all_pending_tasks()
#
#     if not tasks:
#         internal_logger.info("Нет ожидающих задач.")
#         print('Нет запланированых рассылок')
#         return
#
#     for task in tasks:
#         item_dict, run_time = task
#         run_time = datetime.fromisoformat(run_time)  # Преобразуем строку в datetime
#         if run_time > datetime.now():
#             item = Recipient(**item_dict)  # Создаем объект Recipient из словаря
#             schedule_task(item, run_time)
#
#
# if __name__ == "__main__":
#     run_pending_tasks()  # Запуск восстановления задач в фоне
#     uvicorn.run("main:app", host="0.0.0.0", port=5057, reload=True)
import asyncio
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import logging_setup
from routes import router
from tasks import run_pending_tasks
import asyncio

# Путь к папке с вашими статическими файлами
static_directory = os.path.join(os.path.dirname(__file__), "frontend")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
async def get_index():
    return FileResponse(os.path.join(static_directory, "index.html"))

@app.get("/frontend/{file_name}")
async def get_static_file(file_name: str):
    file_path = os.path.join(static_directory, file_name)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}




async def main():
    """Асинхронный запуск задач и Uvicorn"""
    asyncio.create_task(run_pending_tasks())  # Запускаем задачи в фоне

    config = uvicorn.Config("main:app", host="0.0.0.0", port=5057, loop="asyncio")
    server = uvicorn.Server(config)

    await server.serve()  # Асинхронный запуск сервера

if __name__ == "__main__":
    asyncio.run(main())

# if __name__ == "__main__":
#     run_pending_tasks()
#     uvicorn.run("main:app", host="0.0.0.0", port=5057)

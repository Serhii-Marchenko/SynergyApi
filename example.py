# from pprint import pprint
# import requests
#
# Пример отправки данных
# url = 'http://127.0.0.1:8000/api/send'
# headers = {"Content-Type": "application/json"}
#
# data = {
#     "restName": 'sea_terrace', # Название ресторана (должно строго совпадать с названиями файле bx.py departments)
#     "numberOfVisitsFrom": 3, # выборка по количеству визитов гостя От
#     "numberOfVisitsTo": 7,# выборка по количеству визитов гостя До
#     "dateVisitFrom": '2024-09-20', # выборка по дате визита гостя От
#     "dateVisitTo": '2024-10-20',# выборка по дате визита гостя До
#     "textMessage": 'Текст сообщения', # Текст сообщения
#     "linkImage": 'https://drive.google.com/file/d/1aiJJdgmlqzLbg77NFtotO3nGd-xTa0Py/view?usp=sharing', # Ссылка на изображение
#     "timeToStartSending": "2024-11-04T14:39:00", # Время запуска рассылки
#     "textButton": "Youtube", # Текст отправляемой кнопки (если не передать этот параметр, то сообщение отправится без кнопки)
#     "linkButton": "https://www.youtube.com" # ссылка по которо ведет кнопка (если не передать этот параметр, то сообщение отправится без кнопки)
#
# }
# response = requests.post(url, json=data, headers=headers)
# pprint(response.json())
# # pprint(response.content)

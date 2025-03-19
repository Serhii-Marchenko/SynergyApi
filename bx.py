from collections import Counter
from pprint import pprint

import requests

departments = {'beerteka': 325,
               'Юг': 326,
               'sea_terrace': 371,
               'reef': 372,
               'travelers': 373,
               'roastery': 384,
               'central': 5971,
               'mediterranean': 8204}


def get_chat_ids(rest_name, date_from, date_to):

    url = "https://synergy24.com.ua/rest/81/i5t3wtqmjlwqbjzv/crm.deal.list"
    start = 0
    deals = []
    seen_chats = {}  # Для хранения чатов и их дат

    while True:
        # Параметры для запроса с фильтрацией и пагинацией
        params = {
            # 'filter[UF_DEAL_RESTAURANT]': rest_id,
            'filter[UF_DEAL_RESTAURANT]': rest_name,
            'filter[>=DATE_CREATE]': f'{date_from}T00:00:00',
            'filter[<=DATE_CREATE]': f'{date_to}T00:00:00',
            'filter[CATEGORY_ID]': 33,
            'select[]': ['CONTACT_ID', 'TITLE', 'DATE_CREATE'],
            'start': start  # Параметр для пагинации
        }

        response = requests.get(url, params=params)
        data = response.json()
        # pprint(data)

        if 'result' in data:
            for deal in data['result']:
                title = deal['TITLE']
                date_create = deal['DATE_CREATE'][:10]  # Извлекаем только дату в формате YYYY-MM-DD

                # Проверка, был ли этот chat_id уже добавлен в этот день
                if title not in seen_chats or seen_chats[title] != date_create:
                    deals.append(deal['TITLE'].split(' ')[0])
                    seen_chats[title] = date_create  # Запоминаем chat_id и дату

            if len(data['result']) < 50:
                break
            start += 50
        else:
            break
    return deals


# def get_chat_ids(rest_name, date_from, date_to):
#     # тестовая функция
#     print(rest_name, date_from, date_to)
#     return [337363979, 7262079900, 337363979, 7262079900, 337363979, 7262079900, 337363979, 7262079900, 337363979,
#             7262079900 ]


def filter_items_by_frequency(number_from, number_to, data):
    frequency = Counter(data)
    filtered_items = [item for item, count in frequency.items() if number_from <= count <= number_to]
    return filtered_items


def get_fields_deals():
    url = "https://synergy24.com.ua/rest/81/ln1zhvt56xv81qc9/crm.deal.fields"
    headers = {"Content-Type": "application/json"}
    # data = {
    #     "entityTypeId": 33
    # }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Ошибка создания смарт-процесса ", response.text)



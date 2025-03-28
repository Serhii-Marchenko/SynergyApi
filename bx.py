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




def smart_process_add(date_make_sending,date_visit_from, date_visit_to, visits_from, visits_to, rest_code, successes, failures,create_by):
    url = 'https://synergy24.com.ua/rest/104/fzn209q4nyqatqlw/crm.item.add'
    departments = {'325': 'BEERTEKA',
                   '326': 'YUG',
                   '371': 'TERRACE',
                   '372': 'REEF',
                   '384': 'ROASTERY',
                   '5971': 'CAFE CENTRAL',
                   '8204': ' MEDITERRANEAN'
                   }
    fields = {
        #'id': 10, если UPDATE то указываем id созданного елемента
        'category_id': 122, # обязательное поле, без изменений только 122
        'assigned_by_id': 104, # обязательное поле, без изменений только 104
        'ufCrm_69_1743000543': date_make_sending,#"20.03.2025", # Дата начала рассылки
        'ufCrm_69_1743000528': date_visit_to,#"01.03.2025", # Дата посещения До
        'ufCrm_69_1743000490': date_visit_from, # Дата посещения от
        'ufCrm_69_1743000471': visits_to, # Количество посещений До
        'ufCrm_69_1743000455': visits_from, # Количество посещений от
        'ufCrm_69_1743000405': departments[rest_code], # Название ресторана
        'ufCrm_69_1743000989': successes, # Количество успешных отправок
        'ufCrm_69_1743001024': failures, # Количество неуспешных (бот заблокирован / отписка)
        'ufCrm_69_1743013895': create_by, # Кем создана рассылка
    }

    params = {
        'entityTypeId': 1038, # обязательное поле, без изменений только 1038
        'fields': fields,
        'scope': 'crm'
    }

    try:
        response = requests.post(url=url, json=params)
        response.raise_for_status()
        response_json = response.json()
        print(response_json)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
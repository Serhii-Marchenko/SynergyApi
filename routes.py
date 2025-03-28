from datetime import timedelta

from fastapi import APIRouter
import db_sending
import db_user
from models import Send, User, Recipient, UserPhone,DateCheckRequest,DateCheckResponse
from tasks import schedule_task, execute_task,cancel_scheduled_task,start_task
import logging_setup
from utills import send_telegram_message_with_inline_button

router = APIRouter()
internal_logger = logging_setup.internal_logger


@router.post('/delete-send')
async def delete_send(item: Send):
    # print(item.id)
    result = db_sending.delete_record_by_id(item.id)
    cancel_scheduled_task(str(item.id))  # Отменяем задачу при удалении
    # await cancel_scheduled_task(str(item.id))  # Отменяем задачу при удалении

    internal_logger.info(f"Удалена запись {item.id}" if result else f"Ошибка удаления {item.id}")
    if result:
        return {'success': True}


@router.post('/get-sends')
async def get_sends(item: UserPhone):
    all_data = db_sending.get_all_records_by_phone_number(item.phone)
    departments = {'325': 'BEERTEKA',
                   '326': 'YUG',
                   '371': 'TERRACE',
                   '372': 'REEF',
                   '384': 'ROASTERY',
                   '5971': 'CAFE CENTRAL',
                   '8204': ' MEDITERRANEAN'
                   }
    list_all_data = []
    for item in all_data:
        dict_data = {
            "ID": item[0],
            "Заведение": departments[item[2]],
            "Посещений От": item[3],
            "Посещений До": item[4],
            "Дата посещения От": item[5],
            "Дата посещения До": item[6],
            "Текст сообщения": item[7],
            'Cсылка картинки': item[8],
            'Текст кнопки': item[9],
            'Ссылка кнопки': item[10],
            'Рассылка запланирована на:': item[11],
            'Дата создания': item[12]
        }
        list_all_data.append(dict_data)

    return {'success': True,
            'list': list_all_data}


@router.post("/send-sending")
async def schedule_task_endpoint(item: Recipient):
    id_sending = db_sending.create_record(phone_number=item.phone,
                             rest=item.restName,
                             number_of_visits_from=item.numberOfVisitsFrom,
                             number_of_visits_to=item.numberOfVisitsTo,
                             date_visit_from=item.dateVisitFrom,
                             date_visit_to=item.dateVisitTo,
                             text_message=item.textMessage,
                             link_image=item.linkImage,
                             text_button=item.textButton,
                             link_button=item.linkButton,
                             time_to_start_sending=item.timeToStartSending)
    if item.timeToStartSending:
        # schedule_task(item, item.timeToStartSending,id_sending)
        start_task(item, item.timeToStartSending,id_sending)
        return {"message": f"Задача запланирована на {item.timeToStartSending}"}

    return await execute_task(item,id_sending)


@router.post("/send-code")
async def root(user: User):
    id_tg = db_user.get_user_by_phone(user.phone)
    if id_tg is None:
        return {"success": False}
    else:
        send_telegram_message_with_inline_button(id_tg, f"Ваш код: {user.code}")
        return {"success": True, "id_tg": id_tg}

@router.post('/check-date', response_model=DateCheckResponse)
async def check_date(data: DateCheckRequest):
    date_from_front = data.date
    last_date = db_sending.get_latest_scheduled_date_from_db()


    if not last_date:
        return DateCheckResponse(
            allowed=True,
            last_scheduled=None,
            available_date=None
        )

        # ✅ Просто сравниваем timedelta
    if date_from_front - last_date > timedelta(days=2):
        return DateCheckResponse(
            allowed=True,
            last_scheduled=last_date,
            available_date=None
        )
    else:
        available_date = last_date + timedelta(days=3)
        return DateCheckResponse(
            allowed=False,
            last_scheduled=last_date,
            available_date=available_date
        )
from datetime import datetime
import psycopg2
from config import host, port, database, user, password


def create_table_sending():
    db = psycopg2.connect(host=host,
                          port=port,
                          database=database,
                          user=user,
                          password=password
                          )
    cursor = db.cursor()
    cursor.execute(""" CREATE TABLE IF NOT EXISTS sending_tg(
                    id SERIAL PRIMARY KEY,
                    phone_user BIGINT,
                    rest VARCHAR(100),
                    number_of_visits_from INT,
                    number_of_visits_to INT,
                    date_visit_from DATE,
                    date_visit_to DATE,
                    text_message TEXT,
                    link_image TEXT,
                    text_button VARCHAR(100),
                    link_button TEXT,
                    time_to_start_sending TIMESTAMP,
                    date_create TIMESTAMP
        ) """)
    db.commit()
    db.close()


def create_record(phone_number, rest, number_of_visits_from, number_of_visits_to, date_visit_from, date_visit_to,
                  text_message, link_image, text_button, link_button, time_to_start_sending):
    db = psycopg2.connect(host=host,
                          port=port,
                          database=database,
                          user=user,
                          password=password
                          )
    date_create = datetime.now()
    cursor = db.cursor()
    cursor.execute(
        f"INSERT INTO sending_tg(phone_user, rest,number_of_visits_from,number_of_visits_to,date_visit_from,date_visit_to,"
        f"text_message,link_image,text_button,link_button,time_to_start_sending,date_create) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id;",
        (phone_number, rest, number_of_visits_from, number_of_visits_to, date_visit_from, date_visit_to, text_message,
         link_image, text_button, link_button, time_to_start_sending, date_create))
    new_id = cursor.fetchone()[0]
    db.commit()
    db.close()
    return new_id


def get_all_records_by_phone_number(phone_number):
    try:
        # Получаем текущее время в нужном формате
        current_time = datetime.now()

        # Подключаемся к базе данных
        db = psycopg2.connect(host=host,
                              port=port,
                              database=database,
                              user=user,
                              password=password)

        cursor = db.cursor()

        # Выполняем запрос, который выбирает записи по номеру телефона и проверяет поле time_to_start_sending
        cursor.execute(
            """
            SELECT * FROM sending_tg
            WHERE phone_user = %s AND time_to_start_sending > %s
            """,
            (phone_number, current_time)
        )

        # Получаем все записи, которые соответствуют условиям
        info = cursor.fetchall()
        db.commit()
        db.close()

        return info
    except Exception as e:
        print(f"Error: {e}")
        return []


def delete_record_by_id(record_id):
    try:
        db = psycopg2.connect(host=host,
                              port=port,
                              database=database,
                              user=user,
                              password=password
                              )

        cursor = db.cursor()
        cursor.execute(
            "DELETE FROM sending_tg WHERE id = %s",
            (record_id,))
        db.commit()
        db.close()
        return True
    except Exception as e:
        return f"Error: {e}"


def get_all_pending_tasks():
    """Извлекает все ожидающие задачи из базы данных."""
    try:
        # Устанавливаем соединение с базой данных
        conn = psycopg2.connect(host=host,
                                port=port,
                                database=database,
                                user=user,
                                password=password
                                )
        cursor = conn.cursor()

        # Получаем все задачи, где время отправки больше текущего времени
        query = """
        SELECT id, phone_user, rest, number_of_visits_from, number_of_visits_to, 
               date_visit_from, date_visit_to, text_message, link_image, text_button, 
               link_button, time_to_start_sending, date_create
        FROM sending_tg
        WHERE time_to_start_sending > %s
        ORDER BY time_to_start_sending
        """
        # Время для фильтрации задач (текущая дата и время)
        current_time = datetime.now()

        # Выполняем запрос
        cursor.execute(query, (current_time,))
        tasks = cursor.fetchall()

        # Преобразуем данные в удобный для работы вид (список словарей)
        pending_tasks = []
        for task in tasks:
            pending_tasks.append({
                "id": task[0],
                "phone_user": task[1],
                "rest": task[2],
                "number_of_visits_from": task[3],
                "number_of_visits_to": task[4],
                "date_visit_from": task[5],
                "date_visit_to": task[6],
                "text_message": task[7],
                "link_image": task[8],
                "text_button": task[9],
                "link_button": task[10],
                "time_to_start_sending": task[11],
                "date_create": task[12]
            })

        # Закрытие соединения с базой данных
        cursor.close()
        conn.close()

        return pending_tasks

    except Exception as e:
        print(f"Ошибка при извлечении задач: {e}")
        return []
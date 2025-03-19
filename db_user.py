from datetime import datetime
import psycopg2
from config import host, port, database, user, password


def create_table_users():
    db = psycopg2.connect(host=host,
                          port=port,
                          database=database,
                          user=user,
                          password=password
                          )
    cursor = db.cursor()
    cursor.execute(""" CREATE TABLE IF NOT EXISTS sending_tg_user(
                    id SERIAL PRIMARY KEY,
                    id_tg_user BIGINT,
                    phone_number BIGINT,
                    date_create TIMESTAMP
        ) """)
    db.commit()
    db.close()


# create_table_trainee()
def create_user(id_tg_user, phone_number):
    db = psycopg2.connect(host=host,
                          port=port,
                          database=database,
                          user=user,
                          password=password
                          )
    date_create = datetime.now()
    cursor = db.cursor()
    cursor.execute(
        f"INSERT INTO sending_tg_user(id_tg_user,phone_number,date_create) VALUES (%s,%s,%s) RETURNING id;",
        (id_tg_user, phone_number,date_create))
    new_id = cursor.fetchone()[0]
    db.commit()
    db.close()
    return new_id


def get_user_by_phone(phone_number):
    try:
        db = psycopg2.connect(host=host,
                              port=port,
                              database=database,
                              user=user,
                              password=password
                              )
        cursor = db.cursor()
        cursor.execute(
            f"SELECT id_tg_user FROM sending_tg_user WHERE phone_number = %s",
            (phone_number,))
        info = cursor.fetchone()
        db.commit()
        db.close()
        return info
    except:
        return None

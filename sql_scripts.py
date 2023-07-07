import sqlite3
from datetime import datetime, timedelta
from excel_scripts import *
from config import *


def add_user_data_to_db():
    data = read_only()

    for i in data:
        if check_record(i[0]) == False:
            conn = sqlite3.connect(data_base)
            cursor = conn.cursor()

            cursor.execute("INSERT INTO user (login, password, user_id, status, ban_date) VALUES(?, ?, ?, ?, ?)", (i[0], i[1], i[2], 1, None,))

            conn.commit()
            conn.close()


def check_record(login):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    result = cursor.execute("SELECT login FROM user WHERE login = ?", (login,))
    exists = bool(len(result.fetchall()))

    conn.close()

    return exists


def user_data_from_db():
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()
    cursor.execute("SELECT login, password FROM user")
    user_data = cursor.fetchall()

    conn.close()

    return user_data


def add_ban_date(login):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    now = datetime.now()
    ban_date = now.strftime("%H.%d.%m")

    cursor.execute("UPDATE user SET status = ?, ban_date = ? WHERE login = ?", (0, ban_date, login,))

    conn.commit()
    conn.close()


def get_ban_date(login):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()
    cursor.execute("SELECT ban_date FROM user WHERE login = ?", (login,))
    ban_date = cursor.fetchone()[0]

    conn.close()

    return ban_date


def del_ban_date(login):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    cursor.execute("UPDATE user SET status = ?, ban_date = ? WHERE login = ?", (1, None, login,))

    conn.commit()
    conn.close()


def get_login_status(login):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM user WHERE login = ?", (login,))
    log_status = cursor.fetchone()[0]

    conn.close()

    return log_status


def get_user_id(login):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM user WHERE login = ?", (login,))
    user_id = cursor.fetchone()[0]

    conn.close()

    return user_id


def add_date_time(date_app):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    cursor.execute("UPDATE date SET date_time = ? WHERE dt_id = ?", (date_app, 'Previous date',))

    conn.commit()
    conn.close()


def get_prev_date_time():
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()
    cursor.execute("SELECT date_time FROM date WHERE dt_id = ?", ('Previous date',))
    prev_date = cursor.fetchone()[0]

    conn.close()

    return prev_date


def add_user_to_db(user_id):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO noti (user_id, status) VALUES(?, ?)", (user_id, 0,))

    conn.commit()
    conn.close()


def check_user_exists(user_id):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    result = cursor.execute("SELECT user_id FROM noti WHERE user_id = ?", (user_id,))
    user = bool(len(result.fetchall()))

    conn.close()

    return user


def select_users():
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    result = cursor.execute("SELECT user_id FROM noti")
    result = result.fetchall()
    lst = [i[0] for i in result]


    conn.close()

    return lst


def change_user_status(user_id, status):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    cursor.execute("UPDATE noti SET status = ? WHERE user_id = ?", (status, user_id,))

    conn.commit()
    conn.close()


def get_user_status(user_id):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()

    result = cursor.execute("SELECT status FROM noti WHERE user_id = ?", (user_id,))
    stat = result.fetchone()[0]

    conn.close()

    return stat

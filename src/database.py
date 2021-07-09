import sqlite3

from src.configs import DATABASE_PATH

DB = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
DB_CURSOR = DB.cursor()
DB_CURSOR.execute(
    """CREATE TABLE IF NOT EXISTS auth_data (email TEXT, password TEXT)"""
)
DB_CURSOR.execute(
    """CREATE TABLE IF NOT EXISTS bots (email TEXT, password TEXT, sid TEXT, is_valid INTEGER, valid_time INTEGER)"""
)
DB.commit()


def set_auth_data(email: str, password: str):
    DB_CURSOR.execute("""SELECT email FROM auth_data WHERE email=?""", (email,))
    if DB_CURSOR.fetchone() is None:
        DB_CURSOR.execute("""INSERT INTO auth_data VALUES (?, ?)""", (email, password))
        DB.commit()


def get_auth_data():
    DB_CURSOR.execute("""SELECT * FROM auth_data""")
    return DB_CURSOR.fetchall()


def get_bots():
    DB_CURSOR.execute("""SELECT * FROM bots""")
    return DB_CURSOR.fetchall()


def get_bots_cursor():
    DB_CURSOR.execute("""SELECT email, password, is_valid, valid_time FROM bots""")
    return DB_CURSOR


def set_bots(accounts: list):
    if accounts:
        for i in accounts:
            email = i.get("email")
            password = i.get("password")
            sid = i.get("sid")
            is_valid = i.get("isValid")
            valid_time = i.get("validTime")
            DB_CURSOR.execute("""INSERT INTO bots VALUES (?, ?, ?, ?, ?)""", (email, password, sid, is_valid, valid_time))
        DB.commit()


def remove_account(email: str):
    DB_CURSOR.execute("""DELETE FROM auth_data WHERE email=?""", (email,))
    DB.commit()


def remove_bot(email: str):
    DB_CURSOR.execute("""DELETE FROM bots WHERE email=?""", (email,))
    DB.commit()


def clear_table(table_name: str):
    DB_CURSOR.execute(f"""DELETE FROM {table_name}""")
    DB.commit()

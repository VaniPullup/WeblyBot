# db.py
import sqlite3
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "leads.db")


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Таблица заявок
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            course TEXT,
            telegram TEXT,
            user_id INTEGER,
            status TEXT,
            comment TEXT,
            created_at TEXT
        )
    ''')

    # Таблица логов переписки
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dialog_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            sender TEXT,
            message TEXT,
            timestamp TEXT
        )
    ''')

    # Таблица оценок
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ratings (
            user_id INTEGER PRIMARY KEY,
            rating INTEGER,
            date TEXT
        )
    ''')

    conn.commit()
    conn.close()


def save_lead(data: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Проверка, есть ли уже заявки с таким user_id
    cursor.execute("SELECT COUNT(*) FROM leads WHERE user_id = ?", (data.get("user_id"),))
    count = cursor.fetchone()[0]
    status = "повторно" if count > 0 else "новая"

    cursor.execute('''
        INSERT INTO leads (name, phone, course, telegram, user_id, status, comment, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get("name"),
        data.get("phone"),
        data.get("course"),
        data.get("telegram"),
        data.get("user_id"),
        status,
        data.get("comment"),
        datetime.now().strftime("%d.%m.%Y")
    ))
    conn.commit()
    conn.close()


def get_all_leads():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM leads')
    rows = cursor.fetchall()
    conn.close()
    return rows


def search_leads(query: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    like = f"%{query.lower()}%"
    cursor.execute('''
        SELECT * FROM leads
        WHERE LOWER(name) LIKE ? OR LOWER(phone) LIKE ? OR LOWER(course) LIKE ? OR LOWER(comment) LIKE ? OR LOWER(telegram) LIKE ? OR user_id LIKE ?
    ''', (like, like, like, like, like, like))
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_leads_by_date(date: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM leads WHERE created_at = ?', (date,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def save_dialog_log(user_id: int, sender: str, message: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO dialog_logs (user_id, sender, message, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (
        user_id,
        sender,
        message,
        datetime.now().strftime("%d.%m.%Y %H:%M")
    ))
    conn.commit()
    conn.close()


def add_rating(user_id: int, rating: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO ratings (user_id, rating, date) VALUES (?, ?, ?)",
                   (user_id, rating, datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()


def get_user_rating(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT rating FROM ratings WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def get_all_ratings():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, rating FROM ratings")
    results = cursor.fetchall()
    conn.close()
    return results


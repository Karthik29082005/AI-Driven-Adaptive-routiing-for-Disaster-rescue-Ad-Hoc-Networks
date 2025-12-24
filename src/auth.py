import sqlite3
import hashlib
import os

DB_PATH = os.path.join("database", "users.db")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_conn():
    return sqlite3.connect(DB_PATH)

def login_user(username: str, password: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, username, role, full_name
        FROM users
        WHERE username = ? AND password = ?
    """, (username, hash_password(password)))
    row = cur.fetchone()
    conn.close()
    return row

def create_user(username: str, password: str, role: str = "member",
                full_name: str = None, phone: str = None) -> bool:
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO users (username, password, role, full_name, phone)
            VALUES (?, ?, ?, ?, ?)
        """, (username, hash_password(password), role, full_name, phone))
        conn.commit()
        ok = True
    except sqlite3.IntegrityError:
        ok = False
    conn.close()
    return ok

def list_users():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, username, role, full_name, phone FROM users")
    rows = cur.fetchall()
    conn.close()
    return rows

def user_exists(username: str) -> bool:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username = ?", (username,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists

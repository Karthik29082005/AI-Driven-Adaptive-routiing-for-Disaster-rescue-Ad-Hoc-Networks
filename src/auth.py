import sqlite3
import hashlib
import os

# Get the project root directory (parent of src/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "database", "users.db")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_conn():
    # Ensure database directory exists
    db_dir = os.path.dirname(DB_PATH)
    os.makedirs(db_dir, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def login_user(username: str, password: str):
    try:
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
    except sqlite3.Error as e:
        print(f"Database error during login: {e}")
        print(f"Database path: {DB_PATH}")
        return None

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

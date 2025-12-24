import sqlite3
import hashlib
import os

DB_DIR = "database"
DB_PATH = os.path.join(DB_DIR, "users.db")

os.makedirs(DB_DIR, exist_ok=True)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Users table
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL,
    full_name TEXT,
    phone TEXT
)
""")

# Alerts logging
cur.execute("""
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    latitude REAL,
    longitude REAL,
    severity TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# Assignments logging
cur.execute("""
CREATE TABLE IF NOT EXISTS assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_id TEXT,
    assigned_to TEXT,
    alert_id INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# Failures logging
cur.execute("""
CREATE TABLE IF NOT EXISTS failures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_id TEXT,
    reason TEXT,
    latitude REAL,
    longitude REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# RL metrics logging
cur.execute("""
CREATE TABLE IF NOT EXISTS rl_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    episode INTEGER,
    time_taken REAL,
    improvement REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# Default admin
cur.execute("SELECT * FROM users WHERE username = ?", ("admin@gmail.com",))
if not cur.fetchone():
    cur.execute("""
    INSERT INTO users (username, password, role, full_name, phone)
    VALUES (?, ?, ?, ?, ?)
    """, (
        "admin@gmail.com",
        hash_password("admin123"),
        "admin",
        "System Administrator",
        "9999999999"
    ))
    print("Default admin: admin@gmail.com / admin123")

# Default team member
cur.execute("SELECT * FROM users WHERE username = ?", ("team1@gmail.com",))
if not cur.fetchone():
    cur.execute("""
    INSERT INTO users (username, password, role, full_name, phone)
    VALUES (?, ?, ?, ?, ?)
    """, (
        "team1@gmail.com",
        hash_password("team123"),
        "member",
        "Rescue Team 1",
        "8888888888"
    ))
    print("Default member: team1@gmail.com / team123")

conn.commit()
conn.close()
print("Database initialized at", DB_PATH)

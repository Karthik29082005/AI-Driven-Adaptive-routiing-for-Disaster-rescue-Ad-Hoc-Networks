import sqlite3
import os

DB_PATH = os.path.join("database", "users.db")

def _conn():
    return sqlite3.connect(DB_PATH)

def save_alert(lat, lon, sev):
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO alerts (latitude, longitude, severity) VALUES (?, ?, ?)",
        (lat, lon, sev)
    )
    conn.commit()
    alert_id = cur.lastrowid
    conn.close()
    return alert_id

def save_assignment(unit_id, assigned_to, alert_id):
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO assignments (unit_id, assigned_to, alert_id) VALUES (?, ?, ?)",
        (unit_id, assigned_to, alert_id)
    )
    conn.commit()
    conn.close()

def save_failure(unit_id, reason, lat, lon):
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO failures (unit_id, reason, latitude, longitude) VALUES (?, ?, ?, ?)",
        (unit_id, reason, lat, lon)
    )
    conn.commit()
    conn.close()

def save_rl_metric(ep, time_taken, improvement):
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO rl_metrics (episode, time_taken, improvement) VALUES (?, ?, ?)",
        (ep, time_taken, improvement)
    )
    conn.commit()
    conn.close()

def fetch_all(table_name: str):
    conn = _conn()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table_name}")
    rows = cur.fetchall()
    conn.close()
    return rows

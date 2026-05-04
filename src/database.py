import sqlite3
import os
from datetime import datetime
from src.config import DB_PATH

def init_db():
    """Initialize the SQLite database and create the sessions table if it doesn't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            task_description TEXT,
            skill_gap TEXT,
            domain TEXT,
            severity TEXT,
            confidence REAL,
            resource_link TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_session(task_description, skill_gap, domain, severity, confidence, resource_link):
    """Save a new session record to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sessions (timestamp, task_description, skill_gap, domain, severity, confidence, resource_link)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), task_description, skill_gap, domain, severity, confidence, resource_link))
    conn.commit()
    conn.close()

def get_all_sessions():
    """Retrieve all session records from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sessions ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows

def clear_history():
    """Clear all records from the sessions table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM sessions')
    conn.commit()
    conn.close()

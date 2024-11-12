import sqlite3
import logging
from datetime import datetime
from utils import log_event

def initialize_db():
    with sqlite3.connect('chat_history.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS chat_history (
                            session_id TEXT,
                            user_id INTEGER,
                            user_message TEXT,
                            assistant_response TEXT,
                            timestamp TEXT
                        )''')
        conn.commit()

def get_db():
    conn = sqlite3.connect('chat_history.db')
    conn.execute("PRAGMA foreign_keys = ON") 
    return conn

def save_to_db(user_id, user_message, assistant_response, session_id=None):
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO chat_history (session_id, user_id, user_message, assistant_response, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, user_id, user_message, assistant_response, timestamp))
            conn.commit()
            log_event(f"Message saved for user {user_id} at {timestamp}")
        except Exception as e:
            log_event(f"Error saving message for user {user_id}: {str(e)}")
            conn.rollback() 

def get_chat_history_from_db(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_message, assistant_response, timestamp
            FROM chat_history
            WHERE user_id=?
            ORDER BY timestamp ASC
        """, (user_id,))
        rows = cursor.fetchall()
        history = [{"user_message": row[0], "assistant_response": row[1], "timestamp": row[2]} for row in rows]
    return history

def clear_user_chat(user_id):
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM chat_history WHERE user_id=?", (user_id,))
            conn.commit()
            log_event(f"Chat history for user {user_id} has been cleared.")
        except Exception as e:
            log_event(f"Error clearing chat history for user {user_id}: {str(e)}")
            conn.rollback()

initialize_db()

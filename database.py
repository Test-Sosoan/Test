# database.py
import sqlite3
import os
from typing import List, Set

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, role TEXT)''')
    conn.commit()
    
    # Environment variables မှ user ids များကို database ထဲသို့ ထည့်သွင်းခြင်း
    owner_ids = [int(id.strip()) for id in os.environ.get('OWNER_USER_IDS', '').split(',') if id.strip()]
    premium_ids = [int(id.strip()) for id in os.environ.get('PREMIUM_USER_IDS', '').split(',') if id.strip()]
    
    for user_id in owner_ids:
        add_user(user_id, 'owner')
    
    for user_id in premium_ids:
        add_user(user_id, 'premium')
    
    conn.close()

def add_user(user_id: int, role: str = 'user'):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO users (user_id, role) VALUES (?, ?)', (user_id, role))
    conn.commit()
    conn.close()

def get_user_role(user_id: int) -> str:
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT role FROM users WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 'user'

def is_user_registered(user_id: int) -> bool:
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    conn.close()
    return result is not None

def get_users_by_role(role: str) -> List[int]:
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT user_id FROM users WHERE role = ?', (role,))
    results = c.fetchall()
    conn.close()
    return [result[0] for result in results]

# Database initialization
init_db()

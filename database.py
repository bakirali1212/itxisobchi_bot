projects = {}
project_tasks = {}
import sqlite3
from datetime import datetime

# Baza bilan ulanish
conn = sqlite3.connect("project_bot.db")
cursor = conn.cursor()


# talab va taklif jadvali
cursor.execute("""
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    full_name TEXT,
    message TEXT
)
""")
conn.commit()


def save_feedback(user_id, full_name, message):
    cursor.execute(
        "INSERT INTO feedback (user_id, full_name, message) VALUES (?, ?, ?)",
        (user_id, full_name, message)
    )
    conn.commit()


def get_all_feedback():
    cursor.execute("SELECT full_name, message FROM feedback")
    return cursor.fetchall()

# Loyihalar jadvali
cursor.execute("""
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
""")

# Ishlar jadvali
cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    user_id INTEGER,
    username TEXT,
    task_text TEXT,
    created_at TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(id)
)
""")

# Ishchilar jadvali
cursor.execute("""
CREATE TABLE IF NOT EXISTS workers (
    user_id INTEGER PRIMARY KEY,
    full_name TEXT
)
""")

# Foydalanuvchilar jadvali (start bosganda saqlanadi)
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    full_name TEXT,
    username TEXT,
    last_seen TEXT
)
""")
conn.commit()


# === CRUD funksiyalar === #

# Loyiha nomini olish
def get_project_name(project_id):
    cursor.execute("SELECT name FROM projects WHERE id = ?", (project_id,))
    row = cursor.fetchone()
    return row[0] if row else None


# Loyiha qo‘shish
def add_project(name):
    cursor.execute("INSERT INTO projects (name) VALUES (?)", (name,))
    conn.commit()

# Barcha loyihalar
def get_projects():
    cursor.execute("SELECT id, name FROM projects")
    return cursor.fetchall()

# Loyihaga ish yozish
def add_task(project_id, user_id, username, task_text):
    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO tasks (project_id, user_id, username, task_text, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (project_id, user_id, username, task_text, now))
    conn.commit()

# Loyiha bo‘yicha ishlar
def get_tasks_by_project(project_id):
    cursor.execute("""
        SELECT username, task_text, created_at FROM tasks
        WHERE project_id = ?
        ORDER BY created_at DESC
    """, (project_id,))
    return cursor.fetchall()

# Loyihani va unga tegishli ishlarni o‘chirish

def delete_project(project_id):
    # Avval shu loyihaga tegishli barcha ishlarni o‘chiramiz
    cursor.execute("DELETE FROM tasks WHERE project_id = ?", (project_id,))
    # So‘ng loyihani o‘chiramiz
    cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()

# Ishchi qo‘shish
def add_worker(user_id, full_name):
    cursor.execute("INSERT OR IGNORE INTO workers (user_id, full_name) VALUES (?, ?)", (user_id, full_name))
    conn.commit()

# Barcha ishchilar
def get_workers():
    cursor.execute("SELECT user_id, full_name FROM workers")
    return cursor.fetchall()

# Foydalanuvchi ishchilar ro‘yxatida bormi?
def is_worker(user_id):
    cursor.execute("SELECT 1 FROM workers WHERE user_id = ?", (user_id,))
    return cursor.fetchone() is not None

# Ishchi ismini yangilash
def update_worker_name(user_id, full_name):
    cursor.execute("UPDATE workers SET full_name = ? WHERE user_id = ?", (full_name, user_id))
    conn.commit()

# Start bosganda foydalanuvchini saqlash
def save_user(user_id, full_name, username):
    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT OR REPLACE INTO users (user_id, full_name, username, last_seen)
        VALUES (?, ?, ?, ?)
    """, (user_id, full_name, username, now))
    conn.commit()

# Foydalanuvchi start bosganmi?
def is_user_exists(user_id):
    cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone() is not None

# Foydalanuvchi ma'lumotlarini olish
def get_user(user_id):
    cursor.execute("SELECT full_name, username FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone()

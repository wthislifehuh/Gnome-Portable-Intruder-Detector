# database.py
import sqlite3

DB_PATH = 'subscriptions.db'

def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create subscriptions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subscription_code TEXT UNIQUE NOT NULL
    )
    ''')

    # Create chat_ids table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_ids (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subscription_id INTEGER,
        chat_id TEXT UNIQUE NOT NULL,
        FOREIGN KEY (subscription_id) REFERENCES subscriptions(id)
    )
    ''')

    conn.commit()
    conn.close()

class SubscriptionManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def add_subscription(self, subscription_code):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        INSERT OR IGNORE INTO subscriptions (subscription_code) VALUES (?)
        ''', (subscription_code,))
        conn.commit()
        conn.close()

    def add_chat_id(self, subscription_code, chat_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
        SELECT id FROM subscriptions WHERE subscription_code = ?
        ''', (subscription_code,))
        subscription_id = cursor.fetchone()

        if subscription_id:
            cursor.execute('''
            INSERT OR IGNORE INTO chat_ids (subscription_id, chat_id) VALUES (?, ?)
            ''', (subscription_id[0], chat_id))
            conn.commit()
        else:
            print(f"Subscription code {subscription_code} does not exist.")
        
        conn.close()

    def verify_subscription_code(self, subscription_code):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        SELECT * FROM subscriptions WHERE subscription_code = ?
        ''', (subscription_code,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def verify_chat_id(self, chat_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        SELECT * FROM chat_ids WHERE chat_id = ?
        ''', (chat_id,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def get_all_chat_ids(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id FROM chat_ids")
        chat_ids = cursor.fetchall()
        conn.close()
        return [chat_id for (chat_id,) in chat_ids]


# To delete a chat_id : DELETE FROM chat_ids WHERE chat_id = '11169431';
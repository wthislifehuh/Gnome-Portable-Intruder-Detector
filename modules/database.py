import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# SQLite database file path
SQLITE_DB = 'subscriptions_db.sqlite'

def initialize_database():
    conn = sqlite3.connect(SQLITE_DB)
    cursor = conn.cursor()

    # Create subscriptions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS subscriptions (
        subscription_code TEXT PRIMARY KEY,
        password TEXT,
        livefeed TEXT DEFAULT 'http://192.168.1.5:5000'
    )
    ''')

    # Create chat_ids table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_ids (
        subscription_code TEXT,
        chat_id TEXT,
        phone_num TEXT,
        UNIQUE(subscription_code, chat_id),
        FOREIGN KEY(subscription_code) REFERENCES subscriptions(subscription_code) ON DELETE CASCADE
    )
    ''')

    conn.commit()
    conn.close()


class SubscriptionManager:
    def __init__(self, db_path=SQLITE_DB):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = 1")
    
    # =============== Subscription ===============
    def add_subscription(self, subscription_code, password):
        try:
            hashed_password = generate_password_hash(password)
            self.conn.execute(
                'INSERT INTO subscriptions (subscription_code, password) VALUES (?, ?)',
                (subscription_code, hashed_password)
            )
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            print(f"Error adding subscription: {e}")

    def update_password(self, subscription_code, new_password):
        try:
            hashed_password = generate_password_hash(new_password)
            cursor = self.conn.execute(
                'UPDATE subscriptions SET password = ? WHERE subscription_code = ?',
                (hashed_password, subscription_code)
            )
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating password: {e}")
            return False

    def verify_password(self, subscription_code, password):
        cursor = self.conn.execute(
            'SELECT password FROM subscriptions WHERE subscription_code = ?',
            (subscription_code,)
        )
        row = cursor.fetchone()
        if row:
            return check_password_hash(row[0], password)
        return False

    def delete_subscription(self, subscription_code):
        self.conn.execute(
            'DELETE FROM subscriptions WHERE subscription_code = ?',
            (subscription_code,)
        )
        self.conn.commit()

    def verify_subscription_code(self, subscription_code):
        cursor = self.conn.execute(
            'SELECT 1 FROM subscriptions WHERE subscription_code = ?',
            (subscription_code,)
        )
        return cursor.fetchone() is not None

    def get_subscription_code_by_chat_id(self, chat_id):
        cursor = self.conn.execute(
            'SELECT subscription_code FROM chat_ids WHERE chat_id = ?',
            (chat_id,)
        )
        row = cursor.fetchone()
        return row[0] if row else None

    def get_all_subscription_ids(self):
        cursor = self.conn.execute(
            'SELECT subscription_code FROM subscriptions'
        )
        return [row[0] for row in cursor.fetchall()]

    # =============== Chat ID and Phone Number ===============
    def add_chat_id(self, subscription_code, chat_id, phone_num=None):
        if not self.verify_subscription_code(subscription_code):
            print(f"Subscription code {subscription_code} does not exist.")
            return False
        try:
            self.conn.execute(
                'INSERT INTO chat_ids (subscription_code, chat_id, phone_num) VALUES (?, ?, ?)',
                (subscription_code, chat_id, phone_num)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            print(f"Chat ID {chat_id} already exists.")
            return False

    def update_phone_num_for_chat_id(self, subscription_code, chat_id, phone_num):
        cursor = self.conn.execute(
            'UPDATE chat_ids SET phone_num = ? WHERE subscription_code = ? AND chat_id = ?',
            (phone_num, subscription_code, chat_id)
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def delete_chat_id(self, subscription_code, chat_id):
        cursor = self.conn.execute(
            'DELETE FROM chat_ids WHERE subscription_code = ? AND chat_id = ?',
            (subscription_code, chat_id)
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def verify_chatID_phoneNum(self, subscription_code, chat_id, phone_num):
        cursor = self.conn.execute(
            'SELECT 1 FROM chat_ids WHERE subscription_code = ? AND chat_id = ? AND phone_num = ?',
            (subscription_code, chat_id, phone_num)
        )
        return cursor.fetchone() is not None

    def verify_chat_id(self, subscription_code, chat_id):
        cursor = self.conn.execute(
            'SELECT 1 FROM chat_ids WHERE subscription_code = ? AND chat_id = ?',
            (subscription_code, chat_id)
        )
        return cursor.fetchone() is not None

    def get_chat_ids_by_subscription_code(self, subscription_code):
        cursor = self.conn.execute(
            'SELECT chat_id, phone_num FROM chat_ids WHERE subscription_code = ?',
            (subscription_code,)
        )
        return [{'chat_id': row[0], 'phone_num': row[1]} for row in cursor.fetchall()]

    # =============== Phone Numbers ===============
    def get_all_phone_nums(self):
        cursor = self.conn.execute(
            'SELECT phone_num FROM chat_ids WHERE phone_num IS NOT NULL'
        )
        return [row[0] for row in cursor.fetchall()]

    def get_phone_nums_by_subscription_code(self, subscription_code):
        cursor = self.conn.execute(
            'SELECT phone_num FROM chat_ids WHERE subscription_code = ? AND phone_num IS NOT NULL',
            (subscription_code,)
        )
        return [row[0] for row in cursor.fetchall()]

    def verify_phone_num(self, subscription_code, phone_num):
        cursor = self.conn.execute(
            'SELECT 1 FROM chat_ids WHERE subscription_code = ? AND phone_num = ?',
            (subscription_code, phone_num)
        )
        return cursor.fetchone() is not None

    # =============== Livefeed ===============
    def add_livefeed(self, subscription_code, livefeed_url):
        self.conn.execute(
            'UPDATE subscriptions SET livefeed = ? WHERE subscription_code = ?',
            (livefeed_url, subscription_code)
        )
        self.conn.commit()

    def get_livefeed(self, subscription_code):
        cursor = self.conn.execute(
            'SELECT livefeed FROM subscriptions WHERE subscription_code = ?',
            (subscription_code,)
        )
        row = cursor.fetchone()
        return row[0] if row else None

    def get_all(self):
        result = []
        cursor = self.conn.execute('SELECT subscription_code, livefeed FROM subscriptions')
        for idx, row in enumerate(cursor.fetchall(), start=1):
            subscription_code, livefeed = row
            result.append(f"{idx}. {subscription_code} | {livefeed or 'No livefeed'}")

            chat_cursor = self.conn.execute(
                'SELECT chat_id FROM chat_ids WHERE subscription_code = ?',
                (subscription_code,)
            )
            for chat_id_row in chat_cursor.fetchall():
                result.append(f"- {chat_id_row[0]}")

        return "\n".join(result)

    def __del__(self):
        self.conn.close()

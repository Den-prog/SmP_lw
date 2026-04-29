import sqlite3

class CustomDatabaseError(Exception):
    pass

class SQLiteDBManager:
    def __init__(self, db_path='db.sqlite3'):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            raise CustomDatabaseError(f"connect error: {e}")

    def disconnect(self):
        if self.conn:
            self.conn.close()

    def create_table(self):
        try:
            query = """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                price REAL NOT NULL
            )
            """
            self.cursor.execute(query)
            self.conn.commit()
        except sqlite3.Error as e:
            raise CustomDatabaseError(f"create table error: {e}")

    def insert_data(self, title, price):
        try:
            query = "INSERT INTO products (title, price) VALUES (?, ?)"
            self.cursor.execute(query, (title, price))
            self.conn.commit()
        except sqlite3.Error as e:
            raise CustomDatabaseError(f"add error: {e}")

    def fetch_all(self):
        try:
            query = "SELECT * FROM products"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise CustomDatabaseError(f"Помилка вибірки даних: {e}")

    def delete_data(self, record_id):
        try:
            query = "DELETE FROM products WHERE id = ?"
            self.cursor.execute(query, (record_id,))
            self.conn.commit()
        except sqlite3.Error as e:
            raise CustomDatabaseError(f"Помилка видалення запису: {e}")
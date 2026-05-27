import sqlite3

class CustomDatabaseError(Exception):
    pass

class DatabaseError(Exception):
    def __init__(self, message, sqlite_exc: sqlite3.Error = None):
        super().__init__(message)
        if sqlite_exc is not None:
            code = getattr(sqlite_exc, 'sqlite_error_code', None) or -1
            self.error_code = code
            self.error_info = (code, str(sqlite_exc))
        else:
            self.error_code = None
            self.error_info = (None, message)

    def __str__(self):
        return (f"{super().__str__()} "
                f"[errorCode={self.error_code}, "
                f"errorInfo={self.error_info}]")


class SQLiteDBManager:
    def __init__(self, db_path='db.sqlite3'):
        self.db_path = db_path
        self.conn: sqlite3.Connection | None = None
        self.cursor: sqlite3.Cursor | None = None
        self._connect()

    def _connect(self):
        try:
            self.conn = sqlite3.connect(self.db_path, isolation_level=None)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            raise CustomDatabaseError(f"connect error: {e}")

    def disconnect(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def begin_transaction(self):
        try:
            self.cursor.execute('BEGIN')
        except sqlite3.Error as e:
            raise DatabaseError(f"begin transaction error: {e}")

    def commit(self):
        try:
            self.cursor.execute('COMMIT')
        except sqlite3.Error as e:
            raise DatabaseError(f"commit error: {e}")

    def rollback(self):
        try:
            self.cursor.execute('ROLLBACK')
        except sqlite3.Error as e:
            raise DatabaseError(f"rollback error: {e}")

    def create_table(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id    INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT    NOT NULL,
                    price REAL    NOT NULL
                )
            """)
        except sqlite3.Error as e:
            raise DatabaseError("Помилка створення таблиці", e)

    def insert_data(self, title: str, price: float):
        try:
            self.cursor.execute(
                "INSERT INTO products (title, price) VALUES (?, ?)",
                (title, price)
            )
        except sqlite3.Error as e:
            raise DatabaseError("Помилка додавання запису", e)

    def insert_many(self, rows: list[tuple]):
        try:
            self.cursor.executemany(
                "INSERT INTO products (title, price) VALUES (?, ?)",
                rows
            )
        except sqlite3.Error as e:
            raise DatabaseError("Помилка масового додавання", e)

    def fetch_all(self) -> list[dict]:
        try:
            self.cursor.execute("SELECT * FROM products")
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            raise DatabaseError("Помилка вибірки даних", e)

    def delete_data(self, record_id: int):
        try:
            self.cursor.execute(
                "DELETE FROM products WHERE id = ?",
                (record_id,)
            )
        except sqlite3.Error as e:
            raise DatabaseError("Помилка видалення запису", e)

    def setup(self) -> dict:
        try:
            self.begin_transaction()
            self.create_table()

            seed_rows = [
                ("Еко-сумка", 25.0),
                ("Зернова кава", 89.5),
                ("Бамбукова зубна щітка", 45.0),
            ]

            self.cursor.execute("SELECT COUNT(*) FROM products")
            count = self.cursor.fetchone()[0]
            if count == 0:
                self.insert_many(seed_rows)

            self.commit()
            return {
                'success': True,
                'message': 'БД та таблиця успішно ініціалізовані.',
                'error_code': None,
                'error_info': None,
            }

        except DatabaseError as e:
            try:
                self.rollback()
            except DatabaseError:
                pass
            return {
                'success': False,
                'message': f'Неможливо створити базу даних: {e}',
                'error_code': e.error_code,
                'error_info': e.error_info,
            }
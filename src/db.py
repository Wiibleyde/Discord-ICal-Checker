import sqlite3

class CommandLog:
    def __init__(self, date, user, command, args=None):
        self.date = date
        self.user = user
        self.command = command
        self.args = args

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS command_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                user TEXT NOT NULL,
                command TEXT NOT NULL,
                args TEXT
            )
        ''')
        self.conn.commit()

    def insert(self, log):
        self.cursor.execute('''
            INSERT INTO command_log (date, user, command, args)
            VALUES (?, ?, ?, ?)
        ''', (log.date, log.user, log.command, log.args))
        self.conn.commit()

    def get_all(self):
        self.cursor.execute('''
            SELECT * FROM command_log
        ''')
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()
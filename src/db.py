import sqlite3

class CommandLog:
    def __init__(self, date, user, command, args=None):
        self.date = date
        self.user = user
        self.command = command
        self.args = args

class Message:
    def __init__(self, message_id:int, name:str):
        self.message_id = message_id
        self.name = name

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
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER NOT NULL,
                name TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def insert_log(self, log:CommandLog):
        self.cursor.execute('''
            INSERT INTO command_log (date, user, command, args)
            VALUES (?, ?, ?, ?)
        ''', (log.date, log.user, log.command, log.args))
        self.conn.commit()

    def get_all_logs(self) -> list:
        self.cursor.execute('''
            SELECT * FROM command_log
        ''')
        return self.cursor.fetchall()
    
    def insert_message(self, message:Message):
        print(message.message_id, message.name)
        self.cursor.execute('''
            INSERT INTO messages (message_id, name)
            VALUES (?, ?)
        ''', (message.message_id, message.name))
        self.conn.commit()

    def update_message(self, message:Message):
        self.cursor.execute('''
            UPDATE messages
            SET name = ?
            WHERE message_id = ?
        ''', (message.name, message.message_id))
        self.conn.commit()

    def get_message(self, name:str) -> Message:
        self.cursor.execute('''
            SELECT * FROM messages
            WHERE name = ?
        ''', (name,))
        return self.cursor.fetchone()

    def delete_message(self, name:str):
        self.cursor.execute('''
            DELETE FROM messages
            WHERE name = ?
        ''', (name,))
        self.conn.commit()

    def close(self):
        self.conn.close()
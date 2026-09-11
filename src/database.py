import sqlite3
from pathlib import Path


DATABASE_FILE = Path("data/chat_memory.db")


class DatabaseManager:

    def __init__(self):

        DATABASE_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.create_tables()

    def connect(self):

        connection = sqlite3.connect(
            DATABASE_FILE
        )

        connection.row_factory = sqlite3.Row

        return connection

    def create_tables(self):

        with self.connect() as connection:

            # Table 1: Chat sessions
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions
                (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    title TEXT NOT NULL,

                    created_at TEXT
                    NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

                    updated_at TEXT
                    NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # Table 2: Messages
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS messages
                (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    session_id INTEGER NOT NULL,

                    role TEXT NOT NULL,

                    content TEXT NOT NULL,

                    created_at TEXT
                    NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY(session_id)
                    REFERENCES sessions(id)
                )
                """
            )
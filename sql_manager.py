import sqlite3


class ConnectionManager:
    """A context manager for sqlite3 connections, allowing use of "with ContextManager as x:"""

    def __init__(self, database: dict):
        self.database = database

    def __enter__(self):
        """This is what is run as the "with" block opens"""

        self.connection = sqlite3.connect(**self.database)
        self.cursor = self.connection.cursor()
        self.cursor.execute("BEGIN;")
        self.cursor.execute('PRAGMA foreign_keys = True;')
        return self

    def __exit__(self, exc_class, exc, traceback):
        """This is what always happens when the "with" block closes, even in case of exceptions."""

        try:
            # Commit any changes before closing.
            self.connection.commit()
        except AttributeError:
            self.cursor.execute("ROLLBACK;")
            return True  # exception handled successfully
        finally:
            self.connection.close()

    def _execute(self, query: str):
        """Returns the result of the SQL query."""

        self.cursor.execute(query)
        return self.cursor.fetchall()


def execute_query(database: dict, query: str):
    """Runs the ConnectionManager as context manager, handling any exceptions and closing connections."""

    with ConnectionManager(database) as cm:
        return (cm._execute(query))

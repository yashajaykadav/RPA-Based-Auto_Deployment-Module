# YASH KADAV
# yashkadav52@gmail.com

import pyodbc
import psycopg2 # 1. Import the new driver
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self):
        # Renamed for clarity
        self.current_config = None

    # 2. FIX: Rename method and add 'db_type' parameter
    def set_config(self, db_type, server, username, password):
        self.current_config = {
            'db_type': db_type,
            'server': server,
            'username': username,
            'password': password
        }

    @contextmanager
    def database_connection(self, database=""):
        if not self.current_config:
            raise ValueError("No server configuration available")

        cfg = self.current_config
        conn = None
        try:
            # 3. FIX: Add logic to handle both database types
            if cfg['db_type'] == "SQL Server":
                db = database or "master"
                conn_str = (
                    f"DRIVER={{SQL Server}};SERVER={cfg['server']};"
                    f"DATABASE={db};UID={cfg['username']};"
                    f"PWD={cfg['password']};TIMEOUT=10"
                )
                conn = pyodbc.connect(conn_str)
            
            elif cfg['db_type'] == "PostgreSQL":
                db = database or "postgres"
                conn = psycopg2.connect(
                    host=cfg['server'],
                    dbname=db,
                    user=cfg['username'],
                    password=cfg['password'],
                    connect_timeout=10
                )
            
            yield conn
        finally:
            if conn:
                conn.close()

    def test_connection(self):
        try:
            with self.database_connection():
                return True, "Connected successfully"
        except Exception as e:
            return False, str(e)

    def get_databases(self):
        """Get list of available databases."""
        cfg = self.current_config
        query = ""
        
        # 4. FIX: Use the correct SQL query based on the database type
        if cfg['db_type'] == "SQL Server":
            query = "SELECT name FROM sys.databases WHERE database_id > 4 AND state = 0 ORDER BY name"
            default_db = "master"
        elif cfg['db_type'] == "PostgreSQL":
            query = "SELECT datname FROM pg_database WHERE datistemplate = false;"
            default_db = "postgres"
        else:
            raise ValueError(f"Unsupported database type: {cfg['db_type']}")

        try:
            with self.database_connection(database=default_db) as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            raise Exception(f"Failed to fetch databases: {e}")
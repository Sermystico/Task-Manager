import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

# We maintain a global connection pool or just a connection object.
# For simplicity and backward compatibility, we use a single connection,
# but we wrap it in a dependency to allow easy injection.

_conn = psycopg.connect(
    host=os.getenv("DB_HOST", "localhost"),
    dbname=os.getenv("DB_NAME", "task_management"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", "postgres"),
    autocommit=True
)

def get_db_connection() -> psycopg.Connection:
    return _conn

import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()  # Carga las variables del archivo .env

def get_db_connection():
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        raise Exception("DATABASE_URL no está definida")
    conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
    return conn

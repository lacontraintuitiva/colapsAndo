import os
import logging
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()
logger = logging.getLogger(__name__)


def get_db_connection():
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        raise Exception("DATABASE_URL no está definida")

    try:
        if 'render.com' in db_url:
            # En Render, necesitamos SSL
            conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor,
                                    sslmode='require')
        else:
            # Desarrollo local
            conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)

        logger.info("Database connection established successfully")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Error connecting to database: {e}")
        raise

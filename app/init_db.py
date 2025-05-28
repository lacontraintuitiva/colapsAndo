from db import get_db_connection
import psycopg2
from psycopg2.errors import DuplicateTable


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Create tables with PostgreSQL specific data types
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name VARCHAR(255),
                role VARCHAR(50) DEFAULT 'user',
                is_active BOOLEAN DEFAULT FALSE,
                activation_token VARCHAR(36),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create projects table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                category VARCHAR(100),
                user_id INTEGER REFERENCES users(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(50) DEFAULT 'draft',
                is_dirty BOOLEAN DEFAULT FALSE,
                last_saved TIMESTAMP
            )
        ''')

        conn.commit()
        print('Tables created successfully!')
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    init_db()
    print('Database initialized!')

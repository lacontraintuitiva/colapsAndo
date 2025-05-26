import sqlite3


def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  role TEXT DEFAULT 'user',
                  status TEXT DEFAULT 'active')''')

    c.execute('''CREATE TABLE IF NOT EXISTS convocados
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  obra TEXT,
                  tipo_participacion TEXT,
                  FOREIGN KEY(user_id) REFERENCES users(id))''')

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Base de datos inicializada.")

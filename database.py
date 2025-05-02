import sqlite3

def get_db():
    db = sqlite3.connect('film_degerlendirme.db')
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    cursor = db.cursor()
    
    # Kullanıcılar tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            birth_date TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Filmler tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            series_title TEXT NOT NULL,
            released_year INTEGER NOT NULL,
            certificate TEXT,
            runtime INTEGER,
            genre TEXT,
            imdb_rating REAL,
            overview TEXT,
            meta_score INTEGER,
            director TEXT,
            star1 TEXT,
            star2 TEXT,
            star3 TEXT,
            star4 TEXT,
            no_of_votes INTEGER,
            gross TEXT
        )
    ''')
    
    # Değerlendirmeler tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            movie_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (movie_id) REFERENCES movies (id)
        )
    ''')
    
    db.commit()
    db.close() 
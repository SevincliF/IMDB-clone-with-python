import sqlite3

def get_db():
    db = sqlite3.connect('film_degerlendirme.db')
    db.row_factory = sqlite3.Row
    return db

def init_db():
    """Veritabanını ve tabloları oluşturur."""
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Filmler tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            series_title TEXT NOT NULL,
            released_year INTEGER NOT NULL,
            certificate TEXT,
            runtime TEXT,
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (movie_id) REFERENCES movies (id)
        )
    ''')
    
    # Kullanıcı film listesi tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_movie_list (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            movie_id INTEGER NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (movie_id) REFERENCES movies (id),
            UNIQUE(user_id, movie_id)
        )
    ''')
    
    db.commit()
    db.close() 
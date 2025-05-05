import bcrypt
from database import get_db
import sqlite3
import re
from datetime import datetime

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_user(username: str, password: str, email: str, first_name: str, last_name: str, birth_date: str) -> dict:
    db = get_db()
    cursor = db.cursor()
    hashed_password = hash_password(password)
    
    try:
        cursor.execute('''
            INSERT INTO users (username, password, email, first_name, last_name, birth_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, hashed_password, email, first_name, last_name, birth_date))
        db.commit()
        user_id = cursor.lastrowid
        return {"id": user_id, "username": username, "email": email}
    except sqlite3.IntegrityError as e:
        raise Exception("Kullanıcı adı veya e-posta zaten kullanımda")
    finally:
        db.close()

def get_user_by_username(username: str) -> dict:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    db.close()
    return dict(user) if user else None

def create_review(user_id: int, movie_id: int, rating: int, comment: str = None) -> dict:
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO reviews (user_id, movie_id, rating, comment)
            VALUES (?, ?, ?, ?)
        ''', (user_id, movie_id, rating, comment))
        db.commit()
        review_id = cursor.lastrowid
        return {"id": review_id, "user_id": user_id, "movie_id": movie_id, "rating": rating, "comment": comment}
    finally:
        db.close()

def get_movie_by_id(movie_id: int) -> dict:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM movies WHERE id = ?', (movie_id,))
    movie = cursor.fetchone()
    db.close()
    return dict(movie) if movie else None

def get_all_movies() -> list:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM movies')
    movies = [dict(row) for row in cursor.fetchall()]
    db.close()
    return movies

def get_user_reviews(user_id: int) -> list:
    """Kullanıcının tüm yorumlarını getirir."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT r.*, m.series_title 
        FROM reviews r
        JOIN movies m ON r.movie_id = m.id
        WHERE r.user_id = ?
        ORDER BY r.created_at DESC
    ''', (user_id,))
    reviews = [dict(row) for row in cursor.fetchall()]
    db.close()
    return reviews

def get_movie_reviews(movie_id: int) -> list:
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM reviews WHERE movie_id = ?', (movie_id,))
    reviews = [dict(row) for row in cursor.fetchall()]
    db.close()
    return reviews

def add_movie_to_list(user_id: int, movie_id: int) -> bool:
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute('''
            INSERT INTO user_movie_list (user_id, movie_id)
            VALUES (?, ?)
        ''', (user_id, movie_id))
        db.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        db.close()

def remove_movie_from_list(user_id: int, movie_id: int) -> bool:
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute('''
            DELETE FROM user_movie_list
            WHERE user_id = ? AND movie_id = ?
        ''', (user_id, movie_id))
        db.commit()
        return cursor.rowcount > 0
    finally:
        db.close()

def get_user_movie_list(user_id: int) -> list:
    """Kullanıcının film listesini getirir."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT m.*, uml.added_at
        FROM movies m
        JOIN user_movie_list uml ON m.id = uml.movie_id
        WHERE uml.user_id = ?
        ORDER BY uml.added_at DESC
    ''', (user_id,))
    movies = [dict(row) for row in cursor.fetchall()]
    db.close()
    return movies

def is_movie_in_user_list(user_id: int, movie_id: int) -> bool:
    """Filmin kullanıcının listesinde olup olmadığını kontrol eder."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT 1 FROM user_movie_list
        WHERE user_id = ? AND movie_id = ?
    ''', (user_id, movie_id))
    result = cursor.fetchone() is not None
    db.close()
    return result

def is_valid_email(email: str) -> bool:
    """E-posta adresinin geçerli formatta olup olmadığını kontrol eder."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def is_valid_date(date_str: str) -> bool:
    """Tarihin geçerli formatta (YYYY-MM-DD) ve mantıklı bir tarih olup olmadığını kontrol eder."""
    try:
        # Tarih formatını kontrol et
        date = datetime.strptime(date_str, '%Y-%m-%d')
        
        # Geçerli bir yıl kontrolü (örneğin 1900-2100 arası)
        if not (1900 <= date.year <= 2100):
            return False
            
        # Geçerli bir ay kontrolü (1-12)
        if not (1 <= date.month <= 12):
            return False
            
        # Geçerli bir gün kontrolü
        if not (1 <= date.day <= 31):
            return False
            
        # Şubat ayı için özel kontrol
        if date.month == 2:
            # Artık yıl kontrolü
            if date.year % 4 == 0 and (date.year % 100 != 0 or date.year % 400 == 0):
                max_days = 29
            else:
                max_days = 28
            if date.day > max_days:
                return False
                
        # 30 günlük aylar için kontrol
        elif date.month in [4, 6, 9, 11] and date.day > 30:
            return False
            
        return True
    except ValueError:
        return False

def search_movies(query: str) -> list:
    """Film adına göre arama yapar."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT * FROM movies 
        WHERE series_title LIKE ? 
        ORDER BY id
    ''', (f'%{query}%',))
    movies = [dict(row) for row in cursor.fetchall()]
    db.close()
    return movies

def filter_movies_by_genre(genre: str) -> list:
    """Türe göre film filtreler."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT * FROM movies 
        WHERE genre LIKE ? 
        ORDER BY series_title
    ''', (f'%{genre}%',))
    movies = [dict(row) for row in cursor.fetchall()]
    db.close()
    return movies

def filter_movies_by_year(start_year: int, end_year: int) -> list:
    """Yıl aralığına göre film filtreler."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT * FROM movies 
        WHERE released_year BETWEEN ? AND ? 
        ORDER BY released_year
    ''', (start_year, end_year))
    movies = [dict(row) for row in cursor.fetchall()]
    db.close()
    return movies

def filter_movies_by_rating(min_rating: float) -> list:
    """Minimum IMDB puanına göre film filtreler."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT * FROM movies 
        WHERE imdb_rating >= ? 
        ORDER BY imdb_rating DESC
    ''', (min_rating,))
    movies = [dict(row) for row in cursor.fetchall()]
    db.close()
    return movies

def get_all_genres() -> list:
    """Veritabanındaki tüm film türlerini listeler."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT DISTINCT genre FROM movies')
    genres = []
    for row in cursor.fetchall():
        # Her film birden fazla türe sahip olabilir, virgülle ayrılmış
        movie_genres = row['genre'].split(', ')
        genres.extend(movie_genres)
    # Tekrarlanan türleri kaldır ve sırala
    genres = sorted(list(set(genres)))
    db.close()
    return genres

def update_review(review_id: int, user_id: int, rating: int, comment: str) -> bool:
    """Kullanıcının yorumunu günceller."""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute('''
            UPDATE reviews 
            SET rating = ?, comment = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND user_id = ?
        ''', (rating, comment, review_id, user_id))
        db.commit()
        return True
    except:
        db.rollback()
        return False
    finally:
        db.close()

def delete_review(review_id: int, user_id: int) -> bool:
    """Kullanıcının yorumunu siler."""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute('''
            DELETE FROM reviews 
            WHERE id = ? AND user_id = ?
        ''', (review_id, user_id))
        db.commit()
        return True
    except:
        db.rollback()
        return False
    finally:
        db.close() 
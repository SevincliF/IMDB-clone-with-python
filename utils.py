import bcrypt
from datetime import datetime
from database import get_db
import sqlite3

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
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM reviews WHERE user_id = ?', (user_id,))
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
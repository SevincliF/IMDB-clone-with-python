import os
from datetime import datetime
from database import init_db, get_db
from sample_movies import SAMPLE_MOVIES
from utils import (
    create_user, get_user_by_username, verify_password,
    create_review, get_movie_by_id, get_all_movies,
    get_user_reviews, get_movie_reviews
)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu():
    print("\n=== Film Değerlendirme Sistemi ===")
    print("1. Giriş Yap")
    print("2. Kayıt Ol")
    print("3. Film Listele")
    print("4. Film Detayı Görüntüle")
    print("5. Değerlendirme Yap")
    print("6. Çıkış")
    print("================================")

def register():
    print("\n=== Kayıt Ol ===")
    username = input("Kullanıcı adı: ")
    password = input("Şifre: ")
    email = input("E-posta: ")
    first_name = input("Ad: ")
    last_name = input("Soyad: ")
    birth_date = input("Doğum tarihi (YYYY-MM-DD): ")
    
    try:
        user = create_user(username, password, email, first_name, last_name, birth_date)
        print("Kayıt başarılı!")
    except Exception as e:
        print(f"Kayıt sırasında hata oluştu: {str(e)}")

def login():
    print("\n=== Giriş Yap ===")
    username = input("Kullanıcı adı: ")
    password = input("Şifre: ")
    
    user = get_user_by_username(username)
    if user and verify_password(password, user['password']):
        print("Giriş başarılı!")
        return user
    else:
        print("Kullanıcı adı veya şifre hatalı!")
        return None

def list_movies():
    print("\n=== Film Listesi ===")
    movies = get_all_movies()
    for movie in movies:
        print(f"{movie['id']}. {movie['series_title']} ({movie['released_year']}) - IMDB: {movie['imdb_rating']}")

def show_movie_details():
    movie_id = int(input("\nFilm ID'sini girin: "))
    movie = get_movie_by_id(movie_id)
    
    if movie:
        print(f"\n=== {movie['series_title']} ===")
        print(f"Yıl: {movie['released_year']}")
        print(f"Tür: {movie['genre']}")
        print(f"Yönetmen: {movie['director']}")
        print(f"Oyuncular: {movie['star1']}, {movie['star2']}, {movie['star3']}, {movie['star4']}")
        print(f"IMDB Puanı: {movie['imdb_rating']}")
        print(f"Metacritic Puanı: {movie['meta_score']}")
        print(f"Özet: {movie['overview']}")
        
        reviews = get_movie_reviews(movie_id)
        if reviews:
            print("\nDeğerlendirmeler:")
            for review in reviews:
                print(f"- {review['rating']}/10 - {review['comment'] if review['comment'] else 'Yorum yok'}")
    else:
        print("Film bulunamadı!")

def make_review(user):
    movie_id = int(input("\nFilm ID'sini girin: "))
    rating = int(input("Puan (1-10): "))
    comment = input("Yorum (opsiyonel): ")
    
    try:
        review = create_review(user['id'], movie_id, rating, comment)
        print("Değerlendirme başarıyla kaydedildi!")
    except Exception as e:
        print(f"Değerlendirme sırasında hata oluştu: {str(e)}")

def main():
    init_db()
    current_user = None
    
    # Örnek filmleri ekle
    db = get_db()
    cursor = db.cursor()
    if cursor.execute('SELECT COUNT(*) FROM movies').fetchone()[0] == 0:
        for movie in SAMPLE_MOVIES:
            cursor.execute('''
                INSERT INTO movies (
                    series_title, released_year, certificate, runtime, genre,
                    imdb_rating, overview, meta_score, director,
                    star1, star2, star3, star4, no_of_votes, gross
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                movie['series_title'], movie['released_year'], movie['certificate'],
                movie['runtime'], movie['genre'], movie['imdb_rating'],
                movie['overview'], movie['meta_score'], movie['director'],
                movie['star1'], movie['star2'], movie['star3'], movie['star4'],
                movie['no_of_votes'], movie['gross']
            ))
        db.commit()
    db.close()
    
    while True:
        clear_screen()
        print_menu()
        
        choice = input("\nSeçiminiz (1-6): ")
        
        if choice == "1":
            current_user = login()
        elif choice == "2":
            register()
        elif choice == "3":
            list_movies()
        elif choice == "4":
            show_movie_details()
        elif choice == "5":
            if current_user:
                make_review(current_user)
            else:
                print("Lütfen önce giriş yapın!")
        elif choice == "6":
            print("Program sonlandırılıyor...")
            break
        else:
            print("Geçersiz seçim!")
        
        input("\nDevam etmek için Enter'a basın...")

if __name__ == "__main__":
    main() 
import os
from database import init_db, get_db
from sample_movies import SAMPLE_MOVIES
from utils import (
    create_user, get_user_by_username, verify_password,
    create_review, get_movie_by_id, get_all_movies,
    get_user_reviews, get_movie_reviews,
    add_movie_to_list, remove_movie_from_list,
    get_user_movie_list, is_movie_in_user_list,
    is_valid_email, is_valid_date,
    search_movies, filter_movies_by_genre,
    filter_movies_by_year, filter_movies_by_rating,
    get_all_genres, update_review, delete_review
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
    print("6. Listem")
    print("7. Yorum Yönetimi")
    print("8. Çıkış")
    print("================================")

def register():
    print("\n=== Kayıt Ol ===")
    
    while True:
        username = input("Kullanıcı adı: ")
        if not username:
            print("Kullanıcı adı boş olamaz!")
            continue
        break
    
    while True:
        password = input("Şifre: ")
        if not password:
            print("Şifre boş olamaz!")
            continue
        break
    
    while True:
        email = input("E-posta: ")
        if not is_valid_email(email):
            print("Geçersiz e-posta formatı! Örnek: kullanici@ornek.com")
            continue
        break
    
    while True:
        first_name = input("Ad: ")
        if not first_name:
            print("Ad boş olamaz!")
            continue
        break
    
    while True:
        last_name = input("Soyad: ")
        if not last_name:
            print("Soyad boş olamaz!")
            continue
        break
    
    while True:
        birth_date = input("Doğum tarihi (YYYY-MM-DD): ")
        if not is_valid_date(birth_date):
            print("Geçersiz tarih formatı! Örnek: 1990-01-01")
            continue
        break
    
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

def list_movies(current_user):
    print("\n=== Film Listesi ===")
    movies = get_all_movies()
    
    for movie in movies:
        print(f"{movie['id']}. {movie['series_title']} ({movie['released_year']}) - IMDB: {movie['imdb_rating']}")
    
    if current_user:
        print("\n1. Film Detayı Görüntüle")
        print("2. Listeme Ekle")
        print("3. Geri Dön")
        
        choice = input("\nSeçiminiz (1-3): ")
        
        if choice == "1":
            show_movie_details()
        elif choice == "2":
            movie_id = int(input("\nFilm ID'sini girin: "))
            movie = get_movie_by_id(movie_id)
            
            if not movie:
                print("Film bulunamadı!")
                return
            
            if is_movie_in_user_list(current_user['id'], movie_id):
                print("Bu film zaten listenizde!")
                return
            
            if add_movie_to_list(current_user['id'], movie_id):
                print(f"{movie['series_title']} filmi listenize eklendi!")
            else:
                print("Film eklenirken bir hata oluştu!")
        elif choice == "3":
            return
        else:
            print("Geçersiz seçim!")
    else:
        print("\n1. Film Detayı Görüntüle")
        print("2. Geri Dön")
        
        choice = input("\nSeçiminiz (1-2): ")
        
        if choice == "1":
            show_movie_details()
        elif choice == "2":
            return
        else:
            print("Geçersiz seçim!")

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

def show_my_list(user):
    print("\n=== Film Listem ===")
    movies = get_user_movie_list(user['id'])
    if not movies:
        print("Listende henüz film bulunmuyor.")
        return
    
    for movie in movies:
        print(f"{movie['id']}. {movie['series_title']} ({movie['released_year']}) - IMDB: {movie['imdb_rating']}")
        print(f"   Eklenme Tarihi: {movie['added_at']}")
    
    print("\n1. Film Ekle")
    print("2. Film Çıkar")
    print("3. Geri Dön")
    
    choice = input("\nSeçiminiz (1-3): ")
    
    if choice == "1":
        add_to_my_list(user)
    elif choice == "2":
        remove_from_my_list(user)
    elif choice == "3":
        return
    else:
        print("Geçersiz seçim!")

def add_to_my_list(user):
    movie_id = int(input("\nFilm ID'sini girin: "))
    movie = get_movie_by_id(movie_id)
    
    if not movie:
        print("Film bulunamadı!")
        return
    
    if is_movie_in_user_list(user['id'], movie_id):
        print("Bu film zaten listenizde!")
        return
    
    if add_movie_to_list(user['id'], movie_id):
        print(f"{movie['series_title']} filmi listenize eklendi!")
    else:
        print("Film eklenirken bir hata oluştu!")

def remove_from_my_list(user):
    movie_id = int(input("\nFilm ID'sini girin: "))
    movie = get_movie_by_id(movie_id)
    
    if not movie:
        print("Film bulunamadı!")
        return
    
    if not is_movie_in_user_list(user['id'], movie_id):
        print("Bu film listenizde bulunmuyor!")
        return
    
    if remove_movie_from_list(user['id'], movie_id):
        print(f"{movie['series_title']} filmi listenizden çıkarıldı!")
    else:
        print("Film çıkarılırken bir hata oluştu!")

def print_search_menu():
    print("\n=== Film Arama ve Filtreleme ===")
    print("1. İsme Göre Ara")
    print("2. Türe Göre Filtrele")
    print("3. Yıla Göre Filtrele")
    print("4. IMDB Puanına Göre Filtrele")
    print("5. Tüm Filmleri Listele")
    print("6. Geri Dön")
    print("================================")

def search_and_filter_movies(current_user):
    while True:
        clear_screen()
        print_search_menu()
        
        choice = input("\nSeçiminiz (1-6): ")
        
        if choice == "1":
            query = input("\nFilm adını girin: ")
            movies = search_movies(query)
            if not movies:
                print("Aramanızla eşleşen film bulunamadı.")
            else:
                print("\n=== Arama Sonuçları ===")
                for movie in movies:
                    print(f"{movie['id']}. {movie['series_title']} ({movie['released_year']}) - IMDB: {movie['imdb_rating']}")
                if current_user:
                    print("\n1. Film Detayı Görüntüle")
                    print("2. Listeme Ekle")
                    print("3. Geri Dön")
                    sub_choice = input("\nSeçiminiz (1-3): ")
                    if sub_choice == "1":
                        show_movie_details()
                    elif sub_choice == "2":
                        movie_id = int(input("\nFilm ID'sini girin: "))
                        movie = get_movie_by_id(movie_id)
                        if movie and add_movie_to_list(current_user['id'], movie_id):
                            print(f"{movie['series_title']} filmi listenize eklendi!")
                        else:
                            print("Film eklenirken bir hata oluştu!")
                    elif sub_choice == "3":
                        continue
                    else:
                        print("Geçersiz seçim!")
        
        elif choice == "2":
            genres = get_all_genres()
            print("\nMevcut türler:")
            for i, genre in enumerate(genres, 1):
                print(f"{i}. {genre}")
            
            try:
                genre_index = int(input("\nTür numarasını girin: ")) - 1
                if 0 <= genre_index < len(genres):
                    movies = filter_movies_by_genre(genres[genre_index])
                    if not movies:
                        print("Bu türde film bulunamadı.")
                    else:
                        print(f"\n=== {genres[genre_index]} Türündeki Filmler ===")
                        for movie in movies:
                            print(f"{movie['id']}. {movie['series_title']} ({movie['released_year']}) - IMDB: {movie['imdb_rating']}")
                else:
                    print("Geçersiz tür numarası!")
            except ValueError:
                print("Geçersiz giriş!")
        
        elif choice == "3":
            try:
                start_year = int(input("\nBaşlangıç yılını girin: "))
                end_year = int(input("Bitiş yılını girin: "))
                if start_year > end_year:
                    print("Başlangıç yılı bitiş yılından büyük olamaz!")
                    continue
                movies = filter_movies_by_year(start_year, end_year)
                if not movies:
                    print(f"{start_year}-{end_year} yılları arasında film bulunamadı.")
                else:
                    print(f"\n=== {start_year}-{end_year} Yılları Arasındaki Filmler ===")
                    for movie in movies:
                        print(f"{movie['id']}. {movie['series_title']} ({movie['released_year']}) - IMDB: {movie['imdb_rating']}")
            except ValueError:
                print("Geçersiz yıl formatı!")
        
        elif choice == "4":
            try:
                min_rating = float(input("\nMinimum IMDB puanını girin (0-10): "))
                if not (0 <= min_rating <= 10):
                    print("Puan 0-10 arasında olmalıdır!")
                    continue
                movies = filter_movies_by_rating(min_rating)
                if not movies:
                    print(f"{min_rating} ve üzeri puana sahip film bulunamadı.")
                else:
                    print(f"\n=== {min_rating} ve Üzeri Puanlı Filmler ===")
                    for movie in movies:
                        print(f"{movie['id']}. {movie['series_title']} ({movie['released_year']}) - IMDB: {movie['imdb_rating']}")
            except ValueError:
                print("Geçersiz puan formatı!")
        
        elif choice == "5":
            list_movies(current_user)
        
        elif choice == "6":
            return
        
        else:
            print("Geçersiz seçim!")
        
        input("\nDevam etmek için Enter'a basın...")

def print_review_management_menu():
    print("\n=== Yorum Yönetimi ===")
    print("1. Yorumları Görüntüle")
    print("2. Yorum Düzenle")
    print("3. Yorum Sil")
    print("4. Geri Dön")
    print("=====================")

def manage_reviews(current_user):
    while True:
        clear_screen()
        print_review_management_menu()
        
        choice = input("\nSeçiminiz (1-4): ")
        
        if choice == "1":
            reviews = get_user_reviews(current_user['id'])
            if not reviews:
                print("\nHenüz yorum yapmamışsınız.")
            else:
                print("\n=== Yorumlarınız ===")
                for review in reviews:
                    print(f"\nFilm: {review['series_title']}")
                    print(f"Puan: {review['rating']}/10")
                    print(f"Yorum: {review['comment']}")
                    print(f"Tarih: {review['created_at']}")
                    print("-" * 50)
        
        elif choice == "2":
            reviews = get_user_reviews(current_user['id'])
            if not reviews:
                print("\nDüzenleyecek yorumunuz bulunmamaktadır.")
            else:
                print("\n=== Yorumlarınız ===")
                for i, review in enumerate(reviews, 1):
                    print(f"\n{i}. Film: {review['series_title']}")
                    print(f"   Puan: {review['rating']}/10")
                    print(f"   Yorum: {review['comment']}")
                    print(f"   Tarih: {review['created_at']}")
                    print("-" * 50)
                
                try:
                    review_index = int(input("\nDüzenlemek istediğiniz yorumun numarasını girin: ")) - 1
                    if 0 <= review_index < len(reviews):
                        review = reviews[review_index]
                        new_rating = int(input(f"Yeni puan (1-10) [{review['rating']}]: ") or review['rating'])
                        new_comment = input(f"Yeni yorum [{review['comment']}]: ") or review['comment']
                        
                        if update_review(review['id'], current_user['id'], new_rating, new_comment):
                            print("Yorum başarıyla güncellendi!")
                        else:
                            print("Yorum güncellenirken bir hata oluştu!")
                    else:
                        print("Geçersiz yorum numarası!")
                except ValueError:
                    print("Geçersiz giriş!")
        
        elif choice == "3":
            reviews = get_user_reviews(current_user['id'])
            if not reviews:
                print("\nSilecek yorumunuz bulunmamaktadır.")
            else:
                print("\n=== Yorumlarınız ===")
                for i, review in enumerate(reviews, 1):
                    print(f"\n{i}. Film: {review['series_title']}")
                    print(f"   Puan: {review['rating']}/10")
                    print(f"   Yorum: {review['comment']}")
                    print(f"   Tarih: {review['created_at']}")
                    print("-" * 50)
                
                try:
                    review_index = int(input("\nSilmek istediğiniz yorumun numarasını girin: ")) - 1
                    if 0 <= review_index < len(reviews):
                        review = reviews[review_index]
                        confirm = input(f"\n'{review['series_title']}' filmine yaptığınız yorumu silmek istediğinizden emin misiniz? (E/H): ")
                        if confirm.upper() == 'E':
                            if delete_review(review['id'], current_user['id']):
                                print("Yorum başarıyla silindi!")
                            else:
                                print("Yorum silinirken bir hata oluştu!")
                    else:
                        print("Geçersiz yorum numarası!")
                except ValueError:
                    print("Geçersiz giriş!")
        
        elif choice == "4":
            return
        
        else:
            print("Geçersiz seçim!")
        
        input("\nDevam etmek için Enter'a basın...")

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
        
        choice = input("\nSeçiminiz (1-8): ")
        
        if choice == "1":
            current_user = login()
        elif choice == "2":
            register()
        elif choice == "3":
            search_and_filter_movies(current_user)
        elif choice == "4":
            show_movie_details()
        elif choice == "5":
            if current_user:
                make_review(current_user)
            else:
                print("Lütfen önce giriş yapın!")
        elif choice == "6":
            if current_user:
                show_my_list(current_user)
            else:
                print("Lütfen önce giriş yapın!")
        elif choice == "7":
            if current_user:
                manage_reviews(current_user)
            else:
                print("Lütfen önce giriş yapın!")
        elif choice == "8":
            print("Program sonlandırılıyor...")
            break
        else:
            print("Geçersiz seçim!")
        
        input("\nDevam etmek için Enter'a basın...")

if __name__ == "__main__":
    main() 
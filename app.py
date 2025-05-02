from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie_review.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Kullanıcı modeli
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    birth_date = db.Column(db.Date)
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    reviews = db.relationship('Review', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Film modeli
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    series_title = db.Column(db.String(200), nullable=False)
    released_year = db.Column(db.Integer)
    certificate = db.Column(db.String(20))
    runtime = db.Column(db.String(20))
    genre = db.Column(db.String(100))
    imdb_rating = db.Column(db.Float)
    overview = db.Column(db.Text)
    meta_score = db.Column(db.Integer)
    director = db.Column(db.String(100))
    star1 = db.Column(db.String(100))
    star2 = db.Column(db.String(100))
    star3 = db.Column(db.String(100))
    star4 = db.Column(db.String(100))
    no_of_votes = db.Column(db.Integer)
    gross = db.Column(db.String(50))
    reviews = db.relationship('Review', backref='movie', lazy=True)

# Yorum modeli
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    movies = Movie.query.all()
    return render_template('index.html', movies=movies)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        birth_date = datetime.strptime(request.form['birth_date'], '%Y-%m-%d')

        if User.query.filter_by(username=username).first():
            flash('Bu kullanıcı adı zaten kullanılıyor.')
            return redirect(url_for('register'))

        user = User(username=username, email=email, first_name=first_name, 
                   last_name=last_name, birth_date=birth_date)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Kayıt başarılı! Şimdi giriş yapabilirsiniz.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Geçersiz kullanıcı adı veya şifre.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    reviews = Review.query.filter_by(movie_id=movie_id).all()
    return render_template('movie_detail.html', movie=movie, reviews=reviews)

@app.route('/review/<int:movie_id>', methods=['POST'])
@login_required
def add_review(movie_id):
    rating = request.form['rating']
    comment = request.form['comment']
    
    # Kullanıcının bu film için daha önce yorum yapıp yapmadığını kontrol et
    existing_review = Review.query.filter_by(user_id=current_user.id, movie_id=movie_id).first()
    if existing_review:
        flash('Bu film için zaten bir değerlendirme yaptınız.')
        return redirect(url_for('movie_detail', movie_id=movie_id))
    
    review = Review(rating=rating, comment=comment, user_id=current_user.id, movie_id=movie_id)
    db.session.add(review)
    db.session.commit()
    flash('Değerlendirmeniz başarıyla eklendi.')
    return redirect(url_for('movie_detail', movie_id=movie_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 
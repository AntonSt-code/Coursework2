from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='user', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    logs = db.relationship('Log', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def __repr__(self):
        return f'<User {self.username}>'

class Author(db.Model):
    __tablename__ = 'authors'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    bio = db.Column(db.Text)
    birth_date = db.Column(db.Date)
    death_date = db.Column(db.Date)
    country = db.Column(db.String(100))
    
    # Relationships
    book_authors = db.relationship('BookAuthor', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def full_name(self):
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        return ' '.join(parts)
    
    def __repr__(self):
        return f'<Author {self.full_name}>'

class Genre(db.Model):
    __tablename__ = 'genres'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    
    # Relationships
    book_genres = db.relationship('BookGenre', backref='genre', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Genre {self.name}>'

class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    original_title = db.Column(db.String(255))
    description = db.Column(db.Text)
    isbn = db.Column(db.String(20), unique=True, nullable=True)  # Змінено: дозволяємо NULL
    language = db.Column(db.String(10), default='uk')
    publisher = db.Column(db.String(200))
    publication_year = db.Column(db.Integer)
    cover_image_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    book_authors = db.relationship('BookAuthor', backref='book', lazy='dynamic', cascade='all, delete-orphan')
    book_genres = db.relationship('BookGenre', backref='book', lazy='dynamic', cascade='all, delete-orphan')
    files = db.relationship('File', backref='book', lazy='dynamic', cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='book', lazy='dynamic', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='book', lazy='dynamic', cascade='all, delete-orphan')
    logs = db.relationship('Log', backref='book', lazy='dynamic')
    
    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return 0
        return sum(r.rating for r in reviews) / len(reviews)
    
    @property
    def reviews_count(self):
        return self.reviews.count()
    
    def __repr__(self):
        return f'<Book {self.title}>'

class BookAuthor(db.Model):
    __tablename__ = 'book_authors'
    
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)
    role = db.Column(db.String(50), default='author')
    order_index = db.Column(db.Integer, default=0)
    
    __table_args__ = (db.UniqueConstraint('book_id', 'author_id', name='_book_author_uc'),)
    
    def __repr__(self):
        return f'<BookAuthor book_id={self.book_id} author_id={self.author_id}>'

class BookGenre(db.Model):
    __tablename__ = 'book_genres'
    
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'), nullable=False)
    
    __table_args__ = (db.UniqueConstraint('book_id', 'genre_id', name='_book_genre_uc'),)
    
    def __repr__(self):
        return f'<BookGenre book_id={self.book_id} genre_id={self.genre_id}>'

class File(db.Model):
    __tablename__ = 'files'
    
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    format = db.Column(db.String(10), nullable=False)
    file_size = db.Column(db.BigInteger)
    checksum = db.Column(db.String(64))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<File {self.format} for book_id={self.book_id}>'

class Favorite(db.Model):
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'book_id', name='_user_book_favorite_uc'),)
    
    def __repr__(self):
        return f'<Favorite user_id={self.user_id} book_id={self.book_id}>'

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200))
    review_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'book_id', name='_user_book_review_uc'),
        db.CheckConstraint('rating >= 1 AND rating <= 5', name='rating_range')
    )
    
    def __repr__(self):
        return f'<Review by user_id={self.user_id} for book_id={self.book_id}>'

class Log(db.Model):
    __tablename__ = 'logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'))
    action = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    
    def __repr__(self):
        return f'<Log {self.action} at {self.created_at}>'
